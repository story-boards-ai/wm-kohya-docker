import os
import shutil
import subprocess

def main():
    # Source directory containing character folders
    source_directory = "/workspace/characters_prep/"

    # Output directory where ZIP files will be saved
    output_directory = "/workspace/output/"

    # Lists to keep track of successful and failed operations
    successful = []
    skipped = []

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Iterate through each character folder in the source directory
    for character_folder in os.listdir(source_directory):
        character_path = os.path.join(source_directory, character_folder)

        # Check if it's a folder
        if os.path.isdir(character_path):

            # Path to the 'model' and 'log' folders inside the character folder
            model_folder_path = os.path.join(character_path, "model")
            log_folder_path = os.path.join(character_path, "log")

            try:
                # Check if both 'model' and 'log' folders exist
                if not (os.path.exists(model_folder_path) and os.path.exists(log_folder_path)):
                    raise Exception("Missing 'model' and/or 'log' folder")

                # Temporary folder to collect files to be zipped
                temp_folder_path = os.path.join(character_path, "temp")
                os.makedirs(temp_folder_path, exist_ok=True)

                # Copy the 'log' folder to the temporary folder
                shutil.copytree(log_folder_path, os.path.join(temp_folder_path, "log"))

                # Check if there are any .safetensor files in the 'model' folder
                safetensor_files = [f for f in os.listdir(model_folder_path) if f.endswith('.safetensor')]
                if not safetensor_files:
                    raise Exception("No .safetensor files found in 'model' folder")

                # Copy all .safetensor files from 'model' to the temporary folder
                for filename in safetensor_files:
                    shutil.copy(os.path.join(model_folder_path, filename), temp_folder_path)

                # Create a ZIP file
                output_zip_path = os.path.join(output_directory, f"{character_folder}.zip")
                shutil.make_archive(output_zip_path[:-4], 'zip', temp_folder_path)

                # Remove the temporary folder
                shutil.rmtree(temp_folder_path)

                # Add to successful list
                successful.append(character_folder)

            except Exception as e:
                skipped.append((character_folder, str(e)))

    # Display summary
    print("Successfully processed and zipped the following character folders:")
    for name in successful:
        print(f" - {name}")

    print("\nSkipped the following character folders:")
    for name, reason in skipped:
        print(f" - {name} (Reason: {reason})")

    # Run the shell command to send all ZIP files, if there are any successful zips
    if successful:
        subprocess.run(["runpodctl", "send", f"{output_directory}*"])

if __name__ == "__main__":
    main()
