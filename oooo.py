import os

directory_path = "C:/Users/simran.kumari/Documents/excelsheetui/ouput_folder/"

# Check if the directory exists
if os.path.exists(directory_path):
    print(f"The directory '{directory_path}' exists.")
    
    # Check if the application has write permissions
    if os.access(directory_path, os.W_OK):
        print(f"The application has write permissions to '{directory_path}'.")
    else:
        print(f"Error: The application does not have write permissions to '{directory_path}'.")
else:
    print(f"Error: The directory '{directory_path}' does not exist.")
