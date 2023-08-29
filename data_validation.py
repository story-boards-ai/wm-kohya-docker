from collections import defaultdict, OrderedDict
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

def validate_character_folders(test, src_dir=None):
    print("----  data validation  ----")
    if test:
        training_data_path = input("Please enter the path to training_data: ").strip()
    else:
        training_data_path = src_dir

    try:
        character_folders = [f for f in os.listdir(training_data_path) if os.path.isdir(os.path.join(training_data_path, f)) and re.match(r"\d", f)]
        character_folders.sort(key=extract_numeric_prefix_with_suffix)
    except FileNotFoundError:
        print(f"Error: Training data directory '{training_data_path}' not found.")
        return 1
    except Exception as e:
        print(f"Error while listing character folders: {e}")
        return 1

    print(f"Found {len(character_folders)} character folders in '{training_data_path}'.")

    # Initialize stats dictionary
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for char_folder in character_folders:
        # Extract information from folder name: INDEX_ETHNICITY_AGE_SEX
        folder_parts = char_folder.split('_')

        # Extract age and sex using negative indexing
        age = folder_parts[-2]
        sex = folder_parts[-1]

        # The remaining parts make up the index and ethnicity
        index = folder_parts[0]
        ethnicity = '_'.join(folder_parts[1:-2])

        # Continue with the rest of your code...
        age_group = f"{int(age)//10 * 10}'s"
        sex_initial = sex[0].lower()  # 'm' for 'male', 'f' for 'female'
        stats[ethnicity][age_group][sex_initial] += 1


    # Calculate and display stats with percentages
    with open("character_stats.txt", "w") as stats_file:
        for ethnicity, age_groups in stats.items():
            # Calculate the total for this ethnicity
            ethnicity_total = sum([sum(sex_count.values()) for sex_count in age_groups.values()])
            
            print(f"\n{ethnicity} (total: {ethnicity_total}) (m/f):")
            stats_file.write(f"{ethnicity} (total: {ethnicity_total}) (m/f):\n")
            
            sorted_age_groups = OrderedDict(sorted(age_groups.items(), key=lambda x: int(x[0].split("'")[0])))
            for age_group, sex_count in sorted_age_groups.items():
                total = sum(sex_count.values())
                male = sex_count.get('m', 0)
                female = sex_count.get('f', 0)
                male_percent = round((male / total) * 100) if total > 0 else 0
                female_percent = round((female / total) * 100) if total > 0 else 0
                print(f"  {age_group}:  {total},  {male_percent}/{female_percent}")
                stats_file.write(f"  {age_group}:  {total},  {male_percent}/{female_percent}\n")

    invalid_folders = []
    for char_folder in character_folders:
        is_valid, error_message = check_folder_validity(os.path.join(training_data_path, char_folder))
        if not is_valid:
            invalid_folders.append((char_folder, error_message))

    if invalid_folders:
        print("Found the following issues with character folders:")
        with open("invalid_folders.txt", "w") as file:
            for folder_name, error_message in invalid_folders:
                print(f"- {folder_name}: {error_message}")
                file.write(f"{folder_name}: {error_message}\n")
        return 1
    else:
        print("All character folders are valid.")
        return 0

if __name__ == '__main__':
    test_mode = True  # Or False, depending on what you want when running this script standalone
    training_data_path = None  # This will get filled in if test_mode is False
    exit_code = validate_character_folders(test_mode, training_data_path)
    exit(exit_code)
