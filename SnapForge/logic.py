import os

from PIL import Image


class ImageProcessor:
    def batch_process(self, directory, prefix=None, start_number=1, extension=".jpg", convert_format=None, quality=None,
                      rename=True):
        extension = extension.lower()
        count = start_number

        for filename in os.listdir(directory):
            if filename.lower().endswith(extension):
                src = os.path.join(directory, filename)

                if rename:
                    new_extension = convert_format.lower() if convert_format else extension
                    if not new_extension.startswith("."):
                        new_extension = f".{new_extension}"

                    dst = os.path.join(directory, f"{prefix}_{count}{new_extension}")

                    while os.path.exists(dst):
                        count += 1
                        dst = os.path.join(directory, f"{prefix}_{count}{new_extension}")

                if convert_format:
                    new_extension = convert_format.lower() if convert_format else extension
                    if not new_extension.startswith("."):
                        new_extension = f".{new_extension}"

                    dst = os.path.join(directory, f"{prefix}_{count}{new_extension}") if rename else src

                    with Image.open(src) as img:
                        if new_extension == ".jpg" and img.mode in ("RGBA", "LA"):
                            img = img.convert("RGB")
                        img.save(dst, quality=quality)

                    if rename:
                        try:
                            os.remove(src)
                        except PermissionError:
                            print(f"无法删除文件 {src}，权限不足或文件被占用。")

                if rename:
                    count += 1

        return count - start_number
