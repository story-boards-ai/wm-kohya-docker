import os
import shutil
from data_validation import validate_character_folders  # Import the function from data_validation.py
import threading

def get_user_input(prompt, output_list):
    output_list[0] = input(prompt).strip().lower()

# Create a list to store user input
user_input = [None]

# Create a thread to get user input
input_thread = threading.Thread(target=get_user_input, args=("Is this a test run? (yes/no): ", user_input))
input_thread.start()

# Wait for 5 seconds for user input
input_thread.join(timeout=5)

# Check if user input was received
if user_input[0] is None:
    print("Timed out waiting for user input. Running hot.")
    is_test = False
else:
    is_test = user_input[0] == 'yes'

# First, perform data validation
src_dir = '/characters_raw'
dest_dir = '/workspace/characters_prep'
validation_result = validate_character_folders(is_test, src_dir)

if validation_result == 0:
    print("Data validation did not pass. Exiting.")
    exit(0)  # Stop the program

def create_workspace_img_folders_and_copy_files():
    try:
        # List character folders in /characters
        character_folders = [f for f in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, f))]
    except FileNotFoundError:
        print(f"Error: Source directory '{src_dir}' not found.")
        return
    except Exception as e:
        print(f"Error while listing character folders: {e}")
        return

    print(f"Found {len(character_folders)} character folders in '{src_dir}'.")

    for char_folder in character_folders:
        # Path to the img folder in the source directory
        img_src_folder = os.path.join(src_dir, char_folder, 'img')

        try:
            # Count the PNG files in the img folder
            png_files = [f for f in os.listdir(img_src_folder) if f.endswith('.png')]
        except FileNotFoundError:
            print(f"Error: img folder '{img_src_folder}' not found for character '{char_folder}'. Skipping...")
            continue
        except Exception as e:
            print(f"Error while listing PNG files in '{img_src_folder}': {e}")
            continue

        num_png_files = len(png_files)
        print(f"Found {num_png_files} PNG files in '{img_src_folder}'.")

        # Calculate the prefix for the new folder name
        try:
            prefix = int(2500/num_png_files)
        except ZeroDivisionError:
            print(f"Error: No PNG files found for character '{char_folder}'. Skipping...")
            continue
        except Exception as e:
            print(f"Error while calculating prefix for '{char_folder}': {e}")
            continue

        # New folder name in the format: prefix_character_label
        new_folder_name = f"{prefix}_{char_folder}"

        # Path to create the new img folder in the destination directory
        img_dest_folder = os.path.join(dest_dir, char_folder, 'img', new_folder_name)

        # Check if the destination img folder already exists; if not, create it
        try:
            if not os.path.exists(img_dest_folder):
                os.makedirs(img_dest_folder)
                print(f"Created destination folder: '{img_dest_folder}'")
            else:
                print(f"Destination folder '{img_dest_folder}' already exists.")
        except Exception as e:
            print(f"Error while creating destination folder '{img_dest_folder}': {e}")
            continue

        # Create the "model" and "log" folders in the same parent directory as "img"
        for sub_folder in ['model', 'log']:
            folder_path = os.path.join(dest_dir, char_folder, sub_folder)
            try:
                os.makedirs(folder_path, exist_ok=True)
                print(f"Ensured existence of folder: '{folder_path}'")
            except Exception as e:
                print(f"Error while ensuring the existence of folder '{folder_path}': {e}")
                continue

        # Copy the PNG files from the source img folder to the new destination img folder
        copied_files = 0
        skipped_files = 0
        for png_file in png_files:
            src_file_path = os.path.join(img_src_folder, png_file)
            dest_file_path = os.path.join(img_dest_folder, png_file)

            try:
                if not os.path.exists(dest_file_path):
                    shutil.copy2(src_file_path, dest_file_path)
                    copied_files = copied_files + 1
                else:
                    print(f"File '{png_file}' already exists in '{dest_file_path}'. Not copying.")
                    skipped_files = skipped_files + 1
            except Exception as e:
                print(f"Error while copying '{png_file}' from '{src_file_path}' to '{dest_file_path}': {e}")
                continue
        print(f"Copied '{copied_files}' new files. Skipped '{skipped_files}'")


# Run the function
create_workspace_img_folders_and_copy_files()
