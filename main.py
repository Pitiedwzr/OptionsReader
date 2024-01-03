import os
import shutil
import xml.etree.ElementTree as ET
import json
import re

valid_item_types = ["avatarAccessory", "MapIcon", "NamePlate", "Ticket", "Trophy", "SystemVoice"]

def extract_info(line):
    try:
        root = ET.fromstring(line)
        item_data = {}
        id_element = root.find(".//name/id")
        item_data["id"] = id_element.text if id_element is not None else None
        
        name_element = root.find(".//name/str")
        item_data["name"] = name_element.text if name_element is not None else None
        
        explain_element = root.find(".//explainText")
        item_data["explainText"] = explain_element.text if explain_element is not None else None

        return root, item_data
    except ET.ParseError:
        pass
    return None

def clean_filename(filename):
    # 移除非法字符
    cleaned_filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    return cleaned_filename

def process_file(file_path):
    print(f"Processing file: {file_path}")
    
    _, file_name = os.path.split(file_path)
    item_type = file_name.split("_")[0].lower()

    if any(item_type.startswith(valid.lower()) for valid in valid_item_types):
        with open(file_path, "r", encoding="utf-8") as file:
            root, item_info = extract_info(file.read())
        
        if item_info:
            # 确保目录存在
            item_type_directory = os.path.join(os.getcwd(), item_type)
            os.makedirs(item_type_directory, exist_ok=True)

            json_path = os.path.join(os.getcwd(), item_type, f"{item_type}.json")
            with open(json_path, "a+", encoding="utf-8") as json_file:
                json.dump(item_info, json_file, ensure_ascii=False)
                json_file.write("\n")
            print(f"File processed successfully. JSON saved at: {json_path}\n")
            # 复制并重命名图片
            image_path_element = root.find(".//image/path")
            if image_path_element is not None:
                image_relative_path = image_path_element.text
                _, image_name = os.path.split(image_relative_path)
                # 清理非法字符
                new_image_name = f"{item_info['id']}_{clean_filename(item_info['name'])}.dds"
                new_image_path = os.path.join(item_type_directory, new_image_name)
                # 构建完整的源文件路径（相对路径）
                full_source_path = os.path.join(os.path.dirname(file_path), image_relative_path)
                
                shutil.copy(full_source_path, new_image_path)
                print(f"Image copied and renamed successfully. New image saved at: {new_image_path}\n")
        else:
            print("File does not meet the conditions.\n")
    else:
        print("File type does not meet the conditions.\n")

folder_path = input("Please enter the folder path: ")

# 遍历文件夹，处理符合条件的XML文件
def process_files(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)
                process_file(file_path)

process_files(folder_path)