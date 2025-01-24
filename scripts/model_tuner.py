import os
import subprocess

# Define paths
raw_dir = "/home/luisvinatea/Dev/Repos/genealogy/data/raw_images"
processed_dir = "/home/luisvinatea/Dev/Repos/genealogy/data/processed"
output_dir = "/home/luisvinatea/Dev/Repos/genealogy/data/tessdata_fine_tuned"

# Iterate through raw images and their corrected text
for file in os.listdir(raw_dir):
    if file.endswith(".png"):
        base_name = os.path.splitext(file)[0]
        img_path = os.path.join(raw_dir, file)
        txt_path = os.path.join(processed_dir, f"{base_name}.txt")

        # Generate box file
        subprocess.run(["tesseract", img_path, base_name, "nobatch", "box.train"])

        # Train the model
        subprocess.run([
            "lstmtraining",
            "--model_output", os.path.join(output_dir, f"{base_name}_fine_tuned"),
            "--continue_from", "/usr/share/tessdata/ita.lstm",
            "--traineddata", "/usr/share/tessdata/ita.traineddata",
            "--old_traineddata", "/usr/share/tessdata/ita.traineddata",
            "--training_listfile", f"{base_name}.lstmf",
            "--max_iterations", "400"
        ])
