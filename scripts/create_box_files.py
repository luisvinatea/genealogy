import os
import subprocess

# Path to the directory containing raw images
raw_images_dir = "/home/luisvinatea/Dev/Repos/genealogy/data/raw_images"
# Path to the directory where box files will be stored for training
output_dir = "/home/luisvinatea/Dev/Repos/genealogy/data/training_data"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Iterate through all image files in the raw_images directory
for file in os.listdir(raw_images_dir):
    if file.endswith(".png"):
        base_name = os.path.splitext(file)[0]
        image_path = os.path.join(raw_images_dir, file)
        box_file_path = os.path.join(output_dir, f"{base_name}.box")

        print(f"Creating box file for {file}...")

        try:
            # Generate box file using Tesseract in training mode
            subprocess.run([
                "tesseract",
                image_path,
                os.path.join(output_dir, base_name),
                "nobatch",
                "box.train"
            ], check=True)

            print(f"Box file created: {box_file_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating box file for {file}: {e}")

print("Box file creation completed for all images!")
