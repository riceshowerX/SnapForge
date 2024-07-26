import os
from PIL import Image

def batch_convert_images(source_directory, target_directory, target_format):
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    os.makedirs(target_directory, exist_ok=True)
    for root, _, files in os.walk(source_directory):
        for file in files:
            file_extension = os.path.splitext(file)[1].lower()
            if file_extension in image_extensions:
                img = Image.open(os.path.join(root, file))
                new_file_name = f"{os.path.splitext(file)[0]}.{target_format}"
                new_file_path = os.path.join(target_directory, new_file_name)
                img.save(new_file_path, target_format.upper())
    return "Batch conversion completed."
