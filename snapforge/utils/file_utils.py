# snapforge/utils/file_utils.py
import os


def get_image_paths(folder_path):
    """获取文件夹中所有图像文件的路径。

    Args:
        folder_path (str): 文件夹路径。

    Returns:
        list: 图像文件路径列表。
    """
    image_paths = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and is_image_file(file_path):
            image_paths.append(file_path)
    return image_paths


def is_image_file(file_path):
    """判断文件是否为图像文件。

    Args:
        file_path (str): 文件路径。

    Returns:
        bool: 是否为图像文件。
    """
    return file_path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))


def rename_file(file_path, new_name_prefix=None, new_name_suffix=None):
    """重命名文件。

    Args:
        file_path (str): 文件路径。
        new_name_prefix (str, optional): 新文件名前缀。Defaults to None.
        new_name_suffix (str, optional): 新文件名后缀。Defaults to None.

    Returns:
        str: 新文件名。
    """
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    new_name = (
            (new_name_prefix or "")
            + name
            + (new_name_suffix or "")
            + ext
    )
    new_file_path = os.path.join(os.path.dirname(file_path), new_name)
    os.rename(file_path, new_file_path)
    return new_file_path
