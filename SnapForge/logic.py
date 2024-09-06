# logic.py
import os
import re
import uuid
from PIL import Image
import logging

# 初始化日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageProcessor:
    def batch_process(self, directory, prefix=None, start_number=1, extension=".jpg", convert_format=None, quality=None, progress_callback=None):
        extension = extension.lower()
        count = start_number
        total_files = 0
        processed_files = 0

        files = os.listdir(directory)  # 提前获取文件列表
        for filename in files:
            if filename.lower().endswith(extension):
                total_files += 1  # 更新 total_files

                src = os.path.join(directory, filename)

                # 设置新的文件扩展名
                new_extension = convert_format.lower() if convert_format else extension
                if not new_extension.startswith("."):
                    new_extension = f".{new_extension}"

                if prefix:
                    valid_filename = re.sub(r'[\\/*?:"<>|]', '_', f"{prefix}_{count}")
                    unique_filename = valid_filename + "_" + str(uuid.uuid4())
                    dst = os.path.join(directory, f"{unique_filename}{new_extension}")

                    # 确保目标文件名唯一
                    while os.path.exists(dst):
                        count += 1
                        valid_filename = re.sub(r'[\\/*?:"<>|]', '_', f"{prefix}_{count}")
                        unique_filename = valid_filename + "_" + str(uuid.uuid4())
                        dst = os.path.join(directory, f"{unique_filename}{new_extension}")
                else:
                    dst = src

                try:
                    if convert_format:
                        with Image.open(src) as img:
                            if new_extension == ".jpg" and img.mode in ("RGBA", "LA"):
                                img = img.convert("RGB")
                            img.save(dst, format=convert_format.upper(), quality=quality or 95)  # 提供默认质量值
                        os.remove(src)
                    else:
                        os.rename(src, dst)
                except (PermissionError, FileNotFoundError) as e:
                    logging.error(f"处理文件 {filename} 时发生错误: {e}")
                    continue

                count += 1
                processed_files += 1
                # 在这里调用 progress_callback
                if progress_callback:
                    progress = int((processed_files / total_files) * 100)
                    progress_callback(progress)

        return count - start_number
