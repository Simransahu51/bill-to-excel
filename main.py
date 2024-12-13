import os
import sys
from openai import OpenAI
import json
import pandas as pd
import requests

client = OpenAI(api_key='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')

from paddleocr import PaddleOCR

import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QDialog,QMessageBox


from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, \
    QDialog, QLabel, QLineEdit

ocr = PaddleOCR(use_angle_cls=True, lang='en')



class DictionaryTable(QWidget):
    def __init__(self, dictionary):
        super().__init__()
        self.dictionary = dictionary
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Dictionary Table')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Add button to show result
        self.showResultButton = QPushButton('Show Result')
        self.showResultButton.clicked.connect(self.showResult)
        layout.addWidget(self.showResultButton)

        self.setLayout(layout)

    def showResult(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Table Result')
        dialog.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()
        tableWidget = QTableWidget()
        tableWidget.setRowCount(len(self.dictionary['service_provider_name']))
        tableWidget.setColumnCount(len(self.dictionary))

        # Set headers from dictionary keys
        headers = list(self.dictionary.keys())
        tableWidget.setHorizontalHeaderLabels(headers)

        # Populate table
        for col, key in enumerate(self.dictionary.keys()):
            for row, value in enumerate(self.dictionary[key]):
                tableWidget.setItem(row, col, QTableWidgetItem(str(value)))

        layout.addWidget(tableWidget)
        dialog.setLayout(layout)
        dialog.exec_()



class AdvancedWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Options")
        self.layout = QVBoxLayout()

        self.btn_add_data = QPushButton("Add Data to be extracted", self)
        self.btn_add_data.clicked.connect(self.show_enter_data_ui)

        self.btn_add = QPushButton("Add", self)
        self.btn_add.clicked.connect(self.add_data)
        self.btn_add.setVisible(False)

        self.btn_finish = QPushButton("Finish", self)
        self.btn_finish.clicked.connect(self.finish)
        self.btn_finish.setVisible(False)

        self.label_enter_data = QLabel("Enter Data to be extracted", self)
        self.label_enter_data.setVisible(False)

        self.line_edit_data = QLineEdit(self)
        self.line_edit_data.setPlaceholderText("Enter data...")
        self.line_edit_data.setVisible(False)

        self.layout.addWidget(self.btn_add_data)
        self.layout.addWidget(self.label_enter_data)
        self.layout.addWidget(self.line_edit_data)
        self.layout.addWidget(self.btn_add)
        self.layout.addWidget(self.btn_finish)

        self.setLayout(self.layout)

        self.data_list = []

    def show_enter_data_ui(self):
        self.label_enter_data.setVisible(True)
        self.line_edit_data.setVisible(True)
        self.btn_add.setVisible(True)
        self.btn_finish.setVisible(True)

    def add_data(self):
        data = self.line_edit_data.text()
        if data:
            self.data_list.append(data)
            print("Data added:", data)
            self.line_edit_data.clear()

    def finish(self):
        print("Final data list:", self.data_list)
        self.close()


class TableWindow(QDialog):
    def __init__(self, dictionary):
        super().__init__()
        self.dictionary = dictionary
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Table Result')
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()
        tableWidget = QTableWidget()
        tableWidget.setRowCount(len(self.dictionary['service provider name']))
        tableWidget.setColumnCount(len(self.dictionary))

        # Set headers from dictionary keys
        headers = list(self.dictionary.keys())
        tableWidget.setHorizontalHeaderLabels(headers)

        # Populate table
        for col, key in enumerate(self.dictionary.keys()):
            for row, value in enumerate(self.dictionary[key]):
                tableWidget.setItem(row, col, QTableWidgetItem(str(value)))

        layout.addWidget(tableWidget)
        self.setLayout(layout)



class FileLoaderUI(QMainWindow):
    def __init__(self):
        super().__init__()



        self.setWindowTitle("Automatic Invoice Reader")
        self.setGeometry(100, 100, 800, 600)  # Changed dimensions to be larger

        # # Adding logo on the top right
        # self.logo_label = QLabel(self)
        # self.logo_label.setGeometry(600, 100, 150, 150)
        # pixmap = QPixmap("the_ai_company2.png")  # Replace "logo.png" with your actual logo file
        # self.logo_label.setPixmap(pixmap)

        self.layout = QVBoxLayout()
        self.gpt_reply = dict()
        self.btn_advanced = QPushButton("Advanced", self)
        self.btn_advanced.clicked.connect(self.show_advanced_window)
        self.layout.addWidget(self.btn_advanced)

        self.label = QLabel("Enter directory path:", self)
        self.label.move(10, 60)

        self.entry = QLineEdit(self)
        self.entry.setGeometry(150, 60, 500, 30)  # Expanded the entry field

        self.browse_button = QPushButton("Browse", self)
        self.browse_button.setGeometry(670, 60, 100, 30)  # Adjusted position
        self.browse_button.clicked.connect(self.browse_directory)

        self.load_button = QPushButton("Load Files", self)
        self.load_button.setGeometry(350, 180, 100, 30)  # Adjusted position
        self.load_button.clicked.connect(self.load_files)
        self.keyword_list = []
        self.bill_images = []

        # Add button to show result

        layout = QVBoxLayout()

        self.showResultButton = QPushButton('Show Result', self)
        self.showResultButton.setGeometry(500, 180, 100, 30)  # Adjusted position
        self.showResultButton.clicked.connect(self.showResult)
        layout.addWidget(self.showResultButton)







    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.entry.setText(directory)

    def showResult(self):
        try:
            response = requests.get("http://127.0.0.1:8000/result")
            if response.status_code == 200:
                self.tableWindow = TableWindow(response.json())
                self.tableWindow.show()
            else:
                QMessageBox.warning(self, "Error", "Failed to get result from server.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            
        if len(self.gpt_reply.keys()) > 0:
            self.tableWindow = TableWindow(self.gpt_reply)
            self.tableWindow.show()

    def show_advanced_window(self):
        advanced_window = AdvancedWindow(self)
        advanced_window.exec_()
        if len(advanced_window.data_list) > 0:
            for elem in advanced_window.data_list:

                self.keyword_list.append(elem)

        print("KEYWORDS:  ", self.keyword_list)


    def load_files(self):
        directory = self.entry.text()
        if directory:
            try:
                response = requests.post("http://127.0.0.1:8000/upload/", json={"path": directory})
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", response.json()["message"])
                else:
                    QMessageBox.warning(self, "Error", "Failed to process files.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Warning", "Please enter a directory path.")
        bill_no = 1
        bill_content_str = ""
        directory = self.entry.text()
        if os.path.isdir(directory):
            files = os.listdir(directory)
            for file in files:
                # print(os.path.join(directory, file))  # You can modify this to do whatever you want with the files
                file_name = os.path.join(directory, file)
                if file_name.endswith(".jpg") or file_name.endswith(".png") or file_name.endswith(".jpeg"):
                    self.bill_images.append(file_name)


        else:
            print("Invalid directory")



        for id, file in enumerate(self.bill_images):

            print("IDX:  ", id)




            img = cv2.imread(file)
            result = ocr.ocr(img, cls=True)
            image_content = ""
            for idx in range(len(result)):
                res = result[idx]
                if res:

                    for line in res:
                        # print(line[1][0])
                        image_content += line[1][0]
                        image_content +=", "
                # else:
                #     print("NO RES")

            if res:

                # print(image_content)
                abc = f"bill {bill_no} : {image_content}"

                # print("ABC:  ", abc)
                bill_content_str += abc
                bill_content_str += "\n"

                bill_no +=1
                # print("#################################################################################")

            # print(bill_content_str)
            # exit()
            bill_content_str+= f". Total {bill_no - 1} bills. \n"
            key_str = "service provider name, address, date, bill number/invoice number, amount, "
            for elem in self.keyword_list:

                key_str += elem
                key_str += ", "

            key_str += "and nature of expense such as food or transportation or cleaning or purchase or shopping or consulting ...."

            # print("KEY str:  ")
            # print(key_str)
            bill_content_str += f"This is output of my OCR while performed inference on few bills. please get insights from this information Return a json with keys: {key_str}.Initialize a dictionary with the keys mentioned and define empty list as values for each keys. Make sure spelling and everything is correct for the keys. Process each bill in the order and find out value for keys mentioned  as follow: {key_str}. If no information obtained for a key, then consider information for that key as ""NA"" which means Not available. Append information for each key into the lists already initialized inside the dictionary. After appending all information for one bill to the dictionary, make sure length of each list present as key of the dictionary is same. If not add ""NA"" to the list which is less in elements and make the length of all lists equal.Return a proper json string after processing all the bills and adding values to dictionary. Always make sure that all lists are having same length and in the end output, all list length should be same as that of number of bills mentioned. Make sure all the value lists are of same length. If not recheck and make all lists of same length"
            if id % 5 == 0 and id > 0:
                print("inside")

                messages = [{"role": "system", "content":bill_content_str}]

                chat = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
                reply = chat.choices[0].message.content

                # print("reply:  ")
                # print(reply)
                reply_dict = json.loads(reply)

                if (id+1) <=5:
                  self.gpt_reply = reply_dict

                  print("FIRST DICT:  ")
                  print(self.gpt_reply)
                  bill_content_str = ""

                else:
                    merged_dict = self.merge_dicts(self.gpt_reply, reply_dict)
                    self.gpt_reply = merged_dict

                    print("OTHER DICT:  ")
                    print(self.gpt_reply)
                    bill_content_str = ""
            elif id == len(self.bill_images) - 1:

                messages = [{"role": "system", "content": bill_content_str}]

                chat = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
                reply = chat.choices[0].message.content

                # print("reply:  ")
                # print(reply)
                reply_dict = json.loads(reply)

                # if idx <= 5:
                #     self.gpt_reply = reply_dict
                #
                # else:
                merged_dict = self.merge_dicts(self.gpt_reply, reply_dict)
                self.gpt_reply = merged_dict
                bill_content_str = ""

                print("FINAL DICT:  ")
                print(self.gpt_reply)




        df = pd.DataFrame(data=self.gpt_reply)

        output_file = 'C:/Users/simran.kumari/Documents/excelsheetui/ouput_folder/expenses.xlsx'
        df.to_excel(output_file, index=False)

        print(f"Excel file '{output_file}' has been created successfully.")

    def merge_dicts(self, dict1, dict2):
        merged_dict = dict1.copy()
        for key, value in dict2.items():
            if key in merged_dict:
                merged_dict[key].extend(value)
            else:
                merged_dict[key] = value
        return merged_dict


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileLoaderUI()
    window.show()
    sys.exit(app.exec_())
