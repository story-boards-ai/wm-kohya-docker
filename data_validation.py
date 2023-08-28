import os
import re

def extract_numeric_prefix_with_suffix(s):
    match = re.match(r"(\d+)([a-z]*)", s.split('_')[0])
    if match:
        return int(match[1]), match[2]
    return None

def check_folder_validity(folder_path):
    img_folder_path = os.path.join(folder_path, 'img')
    
    if not os.path.exists(img_folder_path):
        return False, f"The character doesn't contain an 'img' subfolder."
    
    if not any(os.scandir(img_folder_path)):
        return False, f"The 'img' folder in the character doesn't contain any files."
    
    parent_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f != '.DS_Store']
    if parent_files:
        return False, f"The character base folder contains files: {', '.join(parent_files)}."

    return True, ""

def validate_character_folders():
    training_data_path = input("Please enter the path to training_data: ").strip()

    try:
        character_folders = [f for f in os.listdir(training_data_path) if os.path.isdir(os.path.join(training_data_path, f)) and re.match(r"\d", f)]
        character_folders.sort(key=extract_numeric_prefix_with_suffix)
    except FileNotFoundError:
        print(f"Error: Training data directory '{training_data_path}' not found.")
        return
    except Exception as e:
        print(f"Error while listing character folders: {e}")
        return

    print(f"Found {len(character_folders)} character folders in '{training_data_path}'.")

    invalid_folders = []
    for char_folder in character_folders:
        is_valid, error_message = check_folder_validity(os.path.join(training_data_path, char_folder))
        if not is_valid:
            invalid_folders.append((char_folder, error_message))
    
    if invalid_folders:
        print("Found the following issues with character folders:")
        for folder_name, error_message in invalid_folders:
            print(f"- {folder_name}: {error_message}")
    else:
        print("All character folders are valid.")

validate_character_folders()
