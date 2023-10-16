#!/bin/bash

# Function to activate virtual environment
check_virtual_environment() {
    venv_path="venv"  # Replace with the actual path to your virtual environment

    if [ -n "$VIRTUAL_ENV" ]; then
        echo "Virtual environment is already activated: $VIRTUAL_ENV"
    else
        echo "Activating virtual environment..."
        source "$venv_path/bin/activate"
        if [ $? -eq 0 ]; then
            echo "Virtual environment activated."
        else
            echo "Failed to activate virtual environment. Exiting."
            exit 1
        fi
    fi
}

# Function to validate folder names
is_valid_folder() {
    [[ $1 =~ ^[0-9] ]]
}

# Function to check if "trained" file exists in a folder
is_character_trained() {
    local folder="$1"
    local trained_file="$folder/trained"
    
    if [ -f "$trained_file" ]; then
        echo "Character '$folder' was previously trained."
        return 0  # Character is trained
    else
        return 1  # Character is not trained
    fi
}

# Function to mark a character as trained
mark_character_as_trained() {
    local folder="$1"
    touch "$folder/trained"
}

# Function to extract numeric and suffix parts
extract_numeric_prefix_with_suffix() {
    # Extract the numeric part from the beginning of the folder name
    num_part=$(echo "$1" | grep -o -E '^[0-9]+')
    
    # Check for the 'a' suffix following the numeric part
    suffix_part=$(echo "$1" | grep -o -E '^[0-9]+[a]?[a]' | grep -o -E 'a')
    
    if [[ -n "$suffix_part" ]]; then
        suffix_part=1
    else
        suffix_part=0
    fi
}

# Main Function
start_training_sessions() {
    echo "Is this a test? (y/n): "
    read is_test
    if [ "$is_test" = "y" ]; then
        echo "Please enter the path for base_dir: "
        read base_dir
    else
        base_dir="/workspace/characters_prep"
    fi

    echo "Do you want to train a series [1], a single [2] or specific characters [3]?"
    read train_type

    if [ "$train_type" = "3" ]; then
        echo "Enter character IDs separated by spaces (e.g. '23 27 55 104'):"
        read -a specific_char_ids
    fi

    if [ "$train_type" = "1" ] || [ "$train_type" = "2" ]; then
        echo "Enter the starting character number: "
        read start_char_num
    fi

    # Base command
    cmd_base=("accelerate" "launch"
        "--num_cpu_threads_per_process=2"
        "./sdxl_train_textual_inversion.py"
        "--pretrained_model_name_or_path=/workspace/kohya_ss/model/sd_xl_base_1.0.safetensors"
        "--resolution=768,768"
        "--save_model_as=safetensors"
        "--lr_scheduler_num_cycles=1"
        "--max_data_loader_n_workers=0"
        "--no_half_vae"
        "--enable_bucket"
        "--learning_rate=0.004"
        "--lr_scheduler=constant"
        "--train_batch_size=1"
        "--max_train_steps=2300"
        "--save_every_n_epochs=1"
        "--mixed_precision=bf16"
        "--caption_extension=.txt" 
        "--save_precision=bf16"
        "--optimizer_type=AdamW8bit"
        "--bucket_reso_steps=64"
        "--save_every_n_steps=50"
        "--mem_eff_attn"
        "--xformers"
        "--bucket_no_upscale"
        "--noise_offset=0.0"
        "--num_vectors_per_token=8"
        "--use_object_template")

    # Getting all valid folders
    all_folders=($(ls -d $base_dir/*/))
    character_folders=()

    for f in "${all_folders[@]}"; do
        folder_name=$(basename "$f")
        if is_valid_folder "$folder_name"; then
            character_folders+=("$folder_name")
        fi
    done

    # Sort character_folders if needed (this is a simple lexicographic sort)
    character_folders=($(for i in "${character_folders[@]}"; do echo $i; done | sort))


    # Apply filters based on user input
    filtered_character_folders=()
    for f in "${character_folders[@]}"; do
        extract_numeric_prefix_with_suffix "$f"

        case "$train_type" in
            1)
                # For series
                if [[ "10#$num_part" -ge "10#$start_char_num" ]]; then
                    filtered_character_folders+=("$f")
                fi
                ;;
            2)
                # For single
                if [[ "10#$num_part" -eq "10#$start_char_num" ]]; then
                    filtered_character_folders+=("$f")
                fi
                ;;
            3)
                # For specific characters
                for id in "${specific_char_ids[@]}"; do
                    if [[ "10#$num_part" -eq "10#$id" ]]; then
                        filtered_character_folders+=("$f")
                        break
                    fi
                done
                ;;
        esac
    done



    for char_folder in "${filtered_character_folders[@]}"; do
        if is_character_trained "$char_folder"; then
            continue  # Character is already trained, skip
        fi

        char_path="$base_dir/$char_folder/img"
        model_path="$base_dir/$char_folder/model"
        log_path="$base_dir/$char_folder/log"

        if [[ $char_folder == *"female"* ]]; then
            init_word="woman"
        elif [[ $char_folder == *"male"* ]]; then
            init_word="man"
        else
            init_word="person"
        fi

        # Constructing the command
        cmd=("${cmd_base[@]}"
            "--train_data_dir=$char_path"
            "--output_dir=$model_path"
            "--logging_dir=$log_path"
            "--output_name=$char_folder"
            "--token_string=$char_folder"
            "--init_word=$init_word")

        # Execute command
        if [ "$is_test" != "y" ]; then
            "${cmd[@]}"
            if [ $? -ne 0 ]; then
                echo "Error occurred while processing '$char_folder'."
            else
                echo "Processed '$char_folder' successfully."
                mark_character_as_trained "$char_folder"
            fi
        fi
    done
}

# Main execution starts here
check_virtual_environment
start_training_sessions
