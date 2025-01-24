import os
from pdf2image import convert_from_path
from PIL import Image
from docx import Document

# Path to the raw directory containing PDF, JPG files, and DOCX files
raw_dir = "/home/luisvinatea/Dev/Repos/genealogy/data/raw"
# Path to the output directory for images
output_dir = "/home/luisvinatea/Dev/Repos/genealogy/data/raw_images"
# Path to the processed directory for text files
processed_dir = "/home/luisvinatea/Dev/Repos/genealogy/data/processed"

# Ensure the output and processed directories exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)

# Convert each PDF file in the raw directory to images
for file in os.listdir(raw_dir):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(raw_dir, file)
        base_name = os.path.splitext(file)[0]
        print(f"Converting {file} to images...")
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            # Save each page as an image
            for i, image in enumerate(images):
                image_name = f"{base_name}_page_{i + 1}.png"
                image_path = os.path.join(output_dir, image_name)
                image.save(image_path, "PNG")
                print(f"Saved {image_path}")
        except Exception as e:
            print(f"Error converting {file}: {e}")

# Convert each JPG file in the raw directory to PNG
for file in os.listdir(raw_dir):
    if file.endswith(".jpg") or file.endswith(".jpeg"):
        jpg_path = os.path.join(raw_dir, file)
        base_name = os.path.splitext(file)[0]
        print(f"Converting {file} to PNG...")
        try:
            # Open the JPG image
            with Image.open(jpg_path) as img:
                png_name = f"{base_name}.png"
                png_path = os.path.join(output_dir, png_name)
                # Save as PNG
                img.save(png_path, "PNG")
                print(f"Saved {png_path}")
        except Exception as e:
            print(f"Error converting {file}: {e}")

# Convert each DOCX file in the raw directory to TXT
for file in os.listdir(raw_dir):
    if file.endswith(".docx"):
        docx_path = os.path.join(raw_dir, file)
        base_name = os.path.splitext(file)[0]
        print(f"Converting {file} to TXT...")
        try:
            # Read the DOCX file
            doc = Document(docx_path)
            text_content = "\n".join([para.text for para in doc.paragraphs])
            txt_path = os.path.join(processed_dir, f"{base_name}.txt")
            # Save as TXT
            with open(txt_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(text_content)
                print(f"Saved {txt_path}")
        except Exception as e:
            print(f"Error converting {file}: {e}")

print("PDF, JPG to image, and DOCX to TXT conversion completed!")
