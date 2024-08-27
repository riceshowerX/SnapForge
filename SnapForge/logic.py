import os
import re
import uuid
from PIL import Image


def batch_process(directory, prefix=None, start_number=1, extension=".jpg", convert_format=None, quality=None,
                  progress_callback=None):
    extension = extension.lower()
    count = start_number
    total_files = sum(1 for filename in os.listdir(directory) if filename.lower().endswith(extension))
    processed_files = 0

    if total_files == 0:
        return 0  # 如果没有文件可处理，直接返回

    for filename in os.listdir(directory):
        if filename.lower().endswith(extension):
            src = os.path.join(directory, filename)

            if prefix:
                valid_filename = re.sub(r'[\\/*?:"<>|]', '_', f"{prefix}_{count}")
                unique_filename = valid_filename + "_" + str(uuid.uuid4())
                new_extension = convert_format.lower() if convert_format else extension
                if not new_extension.startswith("."):
                    new_extension = f".{new_extension}"
                dst = os.path.join(directory, f"{unique_filename}{new_extension}")
            else:
                dst = src  # 如果不重命名，则目标路径和源路径相同

            # 处理图片格式转换和质量压缩
            try:
                with Image.open(src) as img:
                    if convert_format:
                        if new_extension == ".jpg" and img.mode in ("RGBA", "LA"):
                            img = img.convert("RGB")
                        img.save(dst, format=convert_format[1:], quality=quality)
                    elif quality is not None:
                        img.save(dst, quality=quality)
                    else:
                        if prefix:
                            os.rename(src, dst)
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                continue

            # 删除源文件 (如果已成功转换或重命名)
            if os.path.exists(dst) and dst != src:
                try:
                    os.remove(src)
                except PermissionError:
                    print(f"无法删除文件 {src}，权限不足或文件被占用。")

            count += 1
            processed_files += 1
            if progress_callback:
                progress = int((processed_files / total_files) * 100)
                progress_callback(progress)  # 调用回调函数

    return count - start_number
