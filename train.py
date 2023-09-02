import os
import subprocess

def check_virtual_environment():
    if "VIRTUAL_ENV" in os.environ:
        print(f"Virtual environment is activated: {os.environ['VIRTUAL_ENV']}")
    else:
        print("Warning: Virtual environment is not activated. It is recommended to activate it.")

def is_valid_folder(name):
    return name[0].isdigit()

def extract_numeric_prefix_with_suffix(s):
    num_part = int(''.join(filter(str.isdigit, s)))
    suffix_part = 1 if 'a' in s.split('_')[0] else 0
    return (num_part, suffix_part)

def start_training_sessions():
    print("Function start_training_sessions() is being executed.")  # Debugging line
    
    is_test = input("Is this a test? (y/n): ").lower().strip()
    print(f"Is this a test?: {is_test}")  # Debugging line
    
    if is_test == 'y':
        base_dir = input("Please enter the path for base_dir: ").strip()
    else:
        base_dir = '/workspace/characters_prep'

    print(f"Base Directory: {base_dir}")  # Debugging line
    
    train_type = input("Do you want to train a series or a single character? (series/single): ").lower().strip()
    print(f"Training Type: {train_type}")  # Debugging line
    
    start_char_num = int(input("Enter the starting character number: "))
    print(f"Starting Character Number: {start_char_num}")  # Debugging line
    
    print("Building base cmd")  # Debugging line
    
    # Base command
    cmd_base = [
        'accelerate', 'launch', 
        '--num_cpu_threads_per_process=2', 
        './sdxl_train_textual_inversion.py',
        '--pretrained_model_name_or_path=/workspace/kohya_ss/model/sd_xl_base_1.0.safetensors',
        '--resolution=768,768',
        '--save_model_as=safetensors',
        '--lr_scheduler_num_cycles=1',
        '--max_data_loader_n_workers=0',
        '--no_half_vae',
        '--learning_rate=0.005',
        '--lr_scheduler=constant',
        '--train_batch_size=1',
        '--max_train_steps=2300',
        '--save_every_n_epochs=1',
        '--mixed_precision=bf16',
        '--save_precision=bf16',
        '--optimizer_type=AdamW8bit',
        '--bucket_reso_steps=64',
        '--save_every_n_steps=50',
        '--save_state',
        '--mem_eff_attn',
        '--xformers',
        '--bucket_no_upscale',
        '--noise_offset=0.0',
        '--num_vectors_per_token=8',
        '--use_object_template'
    ]
    
    print("Attempting to list all folders...")  # Debugging line
    
    try:
        all_folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
        print(f"All Folders: {all_folders}")  # Debugging line
        
        character_folders = [f for f in all_folders if is_valid_folder(f)]
        character_folders.sort(key=extract_numeric_prefix_with_suffix)
    except Exception as e:
        print(f"An exception occurred: {e}")  # Debugging line
        return
    
    if train_type == "single":
        character_folders = [f for f in character_folders if extract_numeric_prefix_with_suffix(f)[0] == start_char_num]
    else:  # series
        character_folders = [f for f in character_folders if extract_numeric_prefix_with_suffix(f)[0] >= start_char_num]

    print(f"Characters to be trained: {character_folders}")  # Debugging line
    
    for char_folder in character_folders:
        print(f"Processing folder: {char_folder}")  # Debugging line

        print(f"starting with: '{char_folder}'")
        char_path = os.path.join(base_dir, char_folder, 'img')
        model_path = os.path.join(base_dir, char_folder, 'model')
        log_path = os.path.join(base_dir, char_folder, 'log')
        print("paths set")

        if "female" in char_folder:
            init_word = "woman"
        elif "male" in char_folder:
            init_word = "man"
        else:
            init_word = "person"

        # Constructing the command with the specific character folder details
        cmd = cmd_base + [
            f'--train_data_dir={char_path}',
            f'--output_dir={model_path}',
            f'--logging_dir={log_path}',
            f'--output_name={char_folder}',
            f'--token_string={char_folder}',
            f'--init_word={init_word}'
        ]

           # Print the command for visibility
        print("Executing command:", " ".join(cmd))  # Debugging line
        
        if is_test == 'y':
            continue
        else:
            print(f"---- Training '{char_folder}' ----")  # Debugging line
            process = subprocess.Popen(cmd)
            process.wait()

            if process.returncode != 0:
                print(f"Error occurred while processing '{char_folder}'.")
            else:
                print(f"Processed '{char_folder}' successfully.")

if __name__ == '__main__':
    check_virtual_environment()
    start_training_sessions()
