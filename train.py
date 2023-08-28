import os
import subprocess

def is_valid_folder(name):
    return name[0].isdigit()

def extract_numeric_prefix_with_suffix(s):
    num_part = int(''.join(filter(str.isdigit, s)))
    suffix_part = 1 if 'a' in s.split('_')[0] else 0
    return (num_part, suffix_part)

def start_training_sessions():
    is_test = input("Is this a test? (y/n): ").lower().strip()
    if is_test == 'y':
        base_dir = input("Please enter the path for base_dir: ").strip()
    else:
        base_dir = '/workspace/characters_prep'
    
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

    try:
        all_folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
        character_folders = [f for f in all_folders if is_valid_folder(f)]
        character_folders.sort(key=extract_numeric_prefix_with_suffix)
    except FileNotFoundError:
        print(f"Error: Base directory '{base_dir}' not found.")
        return

    for char_folder in character_folders:
        char_path = os.path.join(base_dir, char_folder, 'img')
        model_path = os.path.join(base_dir, char_folder, 'model')
        log_path = os.path.join(base_dir, char_folder, 'log')

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
        print("Executing command:", " ".join(cmd))
        
        if is_test == 'y':
            break
        else:
            # Execute the command
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()

            if process.returncode != 0:
                print(f"Error occurred while processing '{char_folder}': {err.decode('utf-8')}")
            else:
                print(f"Processed '{char_folder}' successfully.")

if __name__ == '__main__':
    start_training_sessions()
