import os
import re
from PIL import Image


def batch_process(directory, prefix=None, start_number=1, extension=".jpg", convert_format=None, quality=None,
                  progress_callback=None):
    """
    批量处理图像文件，包括重命名、格式转换和质量压缩。

    Args:
        directory (str): 要处理的图像文件所在的目录。
        prefix (str, optional): 新文件名的前缀。默认为 None，表示不重命名。
        start_number (int, optional): 新文件名的起始编号。默认为 1。
        extension (str, optional): 要处理的文件扩展名。默认为 ".jpg"。
        convert_format (str, optional): 转换后的文件格式，例如 ".png"。默认为 None，表示不转换格式。
        quality (int, optional): 保存图像的质量，适用于 JPEG 格式。默认为 None，表示使用默认质量。
        progress_callback (function, optional): 进度回调函数，接受一个表示进度的整数参数 (0-100)。

    Returns:
        int: 处理的文件数量。
    """

    extension = extension.lower()
    count = start_number
    total_files = sum(1 for filename in os.listdir(directory) if filename.lower().endswith(extension))
    processed_files = 0

    for filename in os.listdir(directory):
        if filename.lower().endswith(extension):
            src = os.path.join(directory, filename)

            if prefix:
                # 验证文件名 - 使用正则表达式替换非法字符
                valid_filename = re.sub(r'[\\/*?:"<>|]', '_', f"{prefix}_{count}")

                new_extension = convert_format.lower() if convert_format else extension
                if not new_extension.startswith("."):
                    new_extension = f".{new_extension}"

                dst = os.path.join(directory, f"{valid_filename}{new_extension}")

                while os.path.exists(dst):
                    count += 1
                    # 确保在循环中也使用验证后的文件名
                    valid_filename = re.sub(r'[\\/*?:"<>|]', '_', f"{prefix}_{count}")
                    dst = os.path.join(directory, f"{valid_filename}{new_extension}")

            # 处理图片格式转换和质量压缩
            if convert_format or quality is not None:
                try:
                    with Image.open(src) as img:
                        if convert_format:
                            if new_extension == ".jpg" and img.mode in ("RGBA", "LA"):
                                img = img.convert("RGB")
                        if quality is not None:
                            img.save(dst, quality=quality)
                        else:
                            img.save(dst)
                except Exception as e:
                    print(f"处理文件 {filename} 时出错: {e}")
                    continue  # 跳过出错的文件

            else:
                if prefix:  # 仅在需要重命名时才移动文件
                    try:
                        os.rename(src, dst)
                    except Exception as e:
                        print(f"重命名文件 {filename} 时出错: {e}")
                        continue  # 跳过出错的文件

            # 删除源文件 (仅在需要重命名且文件已成功处理后)
            if prefix and os.path.exists(dst):
                try:
                    os.remove(src)
                except PermissionError:
                    print(f"无法删除文件 {src}，权限不足或文件被占用。")

            count += 1
            processed_files += 1
            if progress_callback:
                progress = int((processed_files / total_files) * 100)
                progress_callback.emit(progress)  # 使用 emit 发送信号

    return count - start_number