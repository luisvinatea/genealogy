import os
import pytesseract
from PIL import Image

# Paths
raw_images_dir = "/home/luisvinatea/Dev/Repos/genealogy/data/raw_images"
processed_dir = "/home/luisvinatea/Dev/Repos/genealogy/data/processed"

# Function to detect language based on unique characters
def detect_language(text):
    portuguese_unique_chars = set("ãáâàéêíóôõúç")
    italian_unique_chars = set("àèéìòóù")

    text_chars = set(text.lower())

    # Check for overlap with unique characters
    if text_chars & portuguese_unique_chars:
        return "por"  # Portuguese
    elif text_chars & italian_unique_chars:
        return "ita"  # Italian
    else:
        return "lat"  # Broad Latin (fallback)

# Ensure processed directory exists
os.makedirs(processed_dir, exist_ok=True)

# Process each image file in the raw_images directory
for file in os.listdir(raw_images_dir):
    if file.endswith(".png"):
        base_name = os.path.splitext(file)[0]
        img_path = os.path.join(raw_images_dir, file)
        txt_path = os.path.join(processed_dir, f"{base_name}.txt")

        print(f"Processing {file}...")

        try:
            # Open the image
            image = Image.open(img_path)

            # Perform preliminary OCR to detect language
            preliminary_text = pytesseract.image_to_string(image)
            detected_lang = detect_language(preliminary_text)

            print(f"Detected language: {detected_lang}")

            # Perform OCR with the detected language
            text = pytesseract.image_to_string(image, lang=detected_lang)

            # Save the OCR result to a text file
            with open(txt_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(text)

            print(f"Saved OCR results to {txt_path}")
        except Exception as e:
            print(f"Error processing {file}: {e}")

print("OCR processing completed for all images!")
