import os

def batch_rename_files(directory, prefix, start_number=1):
    current_number = start_number
    for root, _, files in os.walk(directory):
        for file in files:
            file_extension = os.path.splitext(file)[1]
            new_name = f"{prefix}{current_number}{file_extension}"
            old_file_path = os.path.join(root, file)
            new_file_path = os.path.join(root, new_name)
            os.rename(old_file_path, new_file_path)
            current_number += 1
    return f"Batch renaming completed. Renamed {current_number - start_number} files."
