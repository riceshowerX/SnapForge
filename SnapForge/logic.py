import os
from PIL import Image


def batch_rename(directory, prefix, start_number=1, extension=".jpg", convert_format=None):
    extension = extension.lower()
    count = start_number
    for filename in os.listdir(directory):
        if filename.lower().endswith(extension):
            src = os.path.join(directory, filename)

            new_extension = convert_format.lower() if convert_format else extension
            if not new_extension.startswith("."):
                new_extension = f".{new_extension}"

            dst = os.path.join(directory, f"{prefix}_{count}{new_extension}")

            while os.path.exists(dst):
                count += 1
                dst = os.path.join(directory, f"{prefix}_{count}{new_extension}")

            if convert_format:
                with Image.open(src) as img:
                    if new_extension == ".jpg" and img.mode in ("RGBA", "LA"):
                        img = img.convert("RGB")
                    elif new_extension == ".png" and img.mode == "RGB":
                        img = img.convert("RGBA")  # 保持透明度
                    img.save(dst, format=new_extension.upper().strip('.'))
                try:
                    os.remove(src)
                except PermissionError:
                    print(f"无法删除文件 {src}，权限不足或文件被占用。")
            else:
                os.rename(src, dst)

            count += 1

    return count - start_number
