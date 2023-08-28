import os
import shutil

def create_workspace_img_folders_and_copy_files():
    # Base directories
    src_dir = '/kohya_ss/characters'
    dest_dir = '/workspace/characters'

    # List character folders in /characters
    character_folders = [f for f in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, f))]

    print(f"Found {len(character_folders)} character folders in '{src_dir}'.")

    for char_folder in character_folders:
        # Path to the img folder in the source directory
        img_src_folder = os.path.join(src_dir, char_folder, 'img')
        
        # Count the PNG files in the img folder
        png_files = [f for f in os.listdir(img_src_folder) if f.endswith('.png')]
        num_png_files = len(png_files)

        print(f"Found {num_png_files} PNG files in '{img_src_folder}'.")
        
        # Calculate the prefix for the new folder name
        prefix = int(2500/num_png_files)
        
        # New folder name in the format: prefix_character_label
        new_folder_name = f"{prefix}_{char_folder}"
        
        # Path to create the new img folder in the destination directory
        img_dest_folder = os.path.join(dest_dir, char_folder, 'img', new_folder_name)
        
        # Check if the destination img folder already exists; if not, create it
        if not os.path.exists(img_dest_folder):
            os.makedirs(img_dest_folder)
            print(f"Created destination folder: '{img_dest_folder}'")
        else:
            print(f"Destination folder '{img_dest_folder}' already exists.")
        
        # Create the "model" and "log" folders in the same parent directory as "img"
        for sub_folder in ['model', 'log']:
            folder_path = os.path.join(dest_dir, char_folder, sub_folder)
            os.makedirs(folder_path, exist_ok=True)
            print(f"Ensured existence of folder: '{folder_path}'")
        
        # Copy the PNG files from the source img folder to the new destination img folder
        for png_file in png_files:
            src_file_path = os.path.join(img_src_folder, png_file)
            dest_file_path = os.path.join(img_dest_folder, png_file)
            
            # Check if the file already exists in the destination; if not, copy it
            if not os.path.exists(dest_file_path):
                shutil.copy2(src_file_path, dest_file_path)
                print(f"Copied '{png_file}' from '{src_file_path}' to '{dest_file_path}'.")
            else:
                print(f"File '{png_file}' already exists in '{dest_file_path}'. Not copying.")

# Run the function
create_workspace_img_folders_and_copy_files()
