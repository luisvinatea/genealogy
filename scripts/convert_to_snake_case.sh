#!/bin/bash

# Directory to process
TARGET_DIR="/home/luisvinatea/Dev/Repos/genealogy"

# Function to convert to snake_case
to_snake_case() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[[:space:]]+/_/g' | sed -E 's/[^a-z0-9._-]+/_/g' | sed 's/__/_/g'
}

# Rename files and directories recursively
rename_files_and_dirs() {
    local dir="$1"
    for entry in "$dir"/*; do
        if [[ -e "$entry" ]]; then
            # Process subdirectories first
            if [[ -d "$entry" ]]; then
                rename_files_and_dirs "$entry"
            fi
            
            # Get the base directory and filename
            base_dir=$(dirname "$entry")
            base_name=$(basename "$entry")
            new_name=$(to_snake_case "$base_name")

            # Rename if the new name is different
            if [[ "$base_name" != "$new_name" ]]; then
                mv -v "$entry" "$base_dir/$new_name"
            fi
        fi
    done
}

# Start processing
rename_files_and_dirs "$TARGET_DIR"
