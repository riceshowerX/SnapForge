# logic.py
import os
from PIL import Image
import logging

class ImageProcessor:
    def batch_process(self, directory, prefix=None, start_number=1, extension=".jpg", convert_format=None, quality=None, progress_callback=None):
        supported_formats = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]
        extension = extension.lower()
        if extension not in supported_formats:
            logging.error(f"不支持的文件格式: {extension}")
            return 0

        files = [f for f in os.listdir(directory) if f.lower().endswith(extension)]
        total_files = len(files)
        processed_files = 0

        for i, filename in enumerate(files):
            file_path = os.path.join(directory, filename)

            # 文件处理
            try:
                image = Image.open(file_path)

                # 重命名文件
                if prefix:
                    new_filename = f"{prefix}_{start_number + i}{extension}"
                    new_file_path = os.path.join(directory, new_filename)
                    image.save(new_file_path)
                else:
                    new_file_path = file_path

                # 格式转换
                if convert_format:
                    new_file_path = new_file_path.replace(extension, f".{convert_format.lower()}")
                    image.save(new_file_path, format=convert_format)

                # 压缩处理
                if quality is not None:
                    image.save(new_file_path, quality=quality)

                processed_files += 1
                if i % 10 == 0 and progress_callback:
                    progress = int((processed_files / total_files) * 100)
                    progress_callback(progress)

            except Exception as e:
                logging.error(f"处理文件 {filename} 时发生错误: {str(e)}")
                continue

        if progress_callback:
            progress_callback(100)

        return processed_files
