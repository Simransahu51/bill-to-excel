import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
from pydantic import BaseModel
import json
import pandas as pd
from paddleocr import PaddleOCR
from openai import OpenAI
import cv2
import requests
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Initialize PaddleOCR and OpenAI clients
ocr = PaddleOCR(use_angle_cls=True, lang='en')
openai_client = OpenAI(api_key='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')

# Define Pydantic models
class Item(BaseModel):
    path: str

# OCR function to process bill images and extract text
def process_bills(directory_path, keyword_list):
    bill_images = []
    bill_content_str = ""
    bill_no = 1

    if os.path.isdir(directory_path):
        files = os.listdir(directory_path)
        for file in files:
            if file.lower().endswith((".jpg", ".png", ".jpeg")):
                file_path = os.path.join(directory_path, file)
                bill_images.append(file_path)

    gpt_reply = {}  # Initialize gpt_reply with an empty dictionary

    for id, file in enumerate(bill_images):
        img = cv2.imread(file)
        result = ocr.ocr(img, cls=True)
        image_content = ""
        for idx in range(len(result)):
            res = result[idx]
            if res:
                for line in res:
                    image_content += line[1][0]
                    image_content += ", "

        if res:
            abc = f"bill {bill_no} : {image_content}"
            bill_content_str += abc
            bill_content_str += "\n"
            bill_no += 1

        bill_content_str += f". Total {bill_no - 1} bills. \n"
        key_str = "service provider name, address, date, bill number/invoice number, amount, "
        for elem in keyword_list:
            key_str += elem
            key_str += ", "

        key_str += "and nature of expense such as food or transportation or cleaning or purchase or shopping or consulting ...."
        bill_content_str += f"This is output of my OCR while performed inference on few bills. please get insights from this information Return a json with keys: {key_str}.Initialize a dictionary with the keys mentioned and define empty list as values for each keys. Make sure spelling and everything is correct for the keys. Process each bill in the order and find out value for keys mentioned  as follow: {key_str}. If no information obtained for a key, then consider information for that key as \"\"NA\"\" which means Not available. Append information for each key into the lists already initialized inside the dictionary. After appending all information for one bill to the dictionary, make sure length of each list present as key of the dictionary is same. If not add \"\"NA\"\" to the list which is less in elements and make the length of all lists equal.Return a proper json string after processing all the bills and adding values to dictionary. Always make sure that all lists are having same length and in the end output, all list length should be same as that of number of bills mentioned. Make sure all the value lists are of same length. If not recheck and make all lists of same length"

        if id % 5 == 0 and id > 0:
            messages = [{"role": "system", "content": bill_content_str}]
            chat = openai_client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
            reply = chat.choices[0].message.content

            try:
                reply_dict = json.loads(reply.decode('utf-8'))
            except UnicodeDecodeError as e:
                print(f"UnicodeDecodeError: {e}")

            if (id+1) <= 5:
                gpt_reply = reply_dict
            else:
                merged_dict = merge_dicts(gpt_reply, reply_dict)
                gpt_reply = merged_dict
            bill_content_str = ""
        elif id == len(bill_images) - 1:
            messages = [{"role": "system", "content": bill_content_str}]
            chat = openai_client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
            reply = chat.choices[0].message.content

            reply_dict = json.loads(reply)
            merged_dict = merge_dicts(gpt_reply, reply_dict)
            gpt_reply = merged_dict
            bill_content_str = ""

    return gpt_reply

# Merge dictionaries
def merge_dicts(dict1, dict2):
    merged_dict = dict1.copy()
    for key, value in dict2.items():
        if key in merged_dict:
            merged_dict[key].extend(value)
        else:
            merged_dict[key] = value
    return merged_dict

# Route to accept file uploads and process bills
@app.post("/upload/")
async def create_upload_files(item: Item):
    directory_path = item.path

    # Log that file processing has started
    logger.info(f"Processing files in directory: {directory_path}")

    # Check if the provided path is a directory
    if not os.path.isdir(directory_path):
        raise HTTPException(status_code=400, detail="Invalid directory path")

    # Load keywords if needed
    keyword_list = ["service provider name", "date", "amount"]
    # Example list of keywords

    try:
        # Process bill images and extract text using OCR and OpenAI
        gpt_reply = process_bills(directory_path, keyword_list)

        # Generate Excel sheet with extracted content
        df = pd.DataFrame(data=gpt_reply)
        output_file = os.path.join(directory_path, 'expenses.xlsx')
        df.to_excel(output_file, index=False)

        # Log that file processing has completed successfully
        logger.info(f"Files processed successfully. Excel file created at: {output_file}")

        return {"message": f"Files processed and content extracted successfully. Excel file created at: {output_file}"}

    except Exception as e:
        logger.error(f"An error occurred during file processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
