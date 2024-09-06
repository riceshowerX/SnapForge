import os
import re
import uuid
from PIL import Image
import logging

# 初始化日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def batch_process(directory, prefix=None, start_number=1, extension=".jpg", convert_format=None, quality=None,
                  progress_callback=None):
    extension = extension.lower()
    count = start_number
    total_files = sum(1 for filename in os.listdir(directory) if filename.lower().endswith(extension))
    processed_files = 0

    if total_files == 0:
        logging.warning("目录中没有可处理的文件。")
        return 0  # 如果没有文件可处理，直接返回

    for filename in os.listdir(directory):
        if filename.lower().endswith(extension):
            src = os.path.join(directory, filename)

            if prefix:
                valid_filename = re.sub(r'[\\/*?:"<>|]', '_', f"{prefix}_{count}")
                unique_filename = valid_filename + "_" + str(uuid.uuid4())
                new_extension = f".{convert_format.lower()}" if convert_format else extension
                dst = os.path.join(directory, f"{unique_filename}{new_extension}")
            else:
                dst = src  # 如果不重命名，则目标路径和源路径相同

            # 处理图片格式转换和质量压缩
            try:
                with Image.open(src) as img:
                    if convert_format:
                        # 如果转换为 JPG 格式且图片包含透明通道，则转换为 RGB
                        if new_extension == ".jpg" and img.mode in ("RGBA", "LA"):
                            img = img.convert("RGB")
                        img.save(dst, format=convert_format.upper(), quality=quality or 95)  # 提供默认质量值
                    elif quality is not None:
                        img.save(dst, quality=quality)
                    else:
                        if prefix:
                            os.rename(src, dst)
            except Exception as e:
                logging.error(f"处理文件 {filename} 时出错: {e}")
                continue

            # 删除源文件 (如果已成功转换或重命名)
            if os.path.exists(dst) and dst != src:
                try:
                    os.remove(src)
                except PermissionError:
                    logging.warning(f"无法删除文件 {src}，权限不足或文件被占用。")

            count += 1
            processed_files += 1
            if progress_callback:
                progress = int((processed_files / total_files) * 100)
                progress_callback(progress)  # 调用回调函数

    return count - start_number
