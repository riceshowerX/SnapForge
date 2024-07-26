import os
from PIL import Image

def batch_compress_images(source_directory, target_directory, quality):
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    os.makedirs(target_directory, exist_ok=True)
    for root, _, files in os.walk(source_directory):
        for file in files:
            file_extension = os.path.splitext(file)[1].lower()
            if file_extension in image_extensions:
                img = Image.open(os.path.join(root, file))
                new_file_path = os.path.join(target_directory, file)
                img.save(new_file_path, quality=quality, optimize=True)
    return "Batch compression completed."
