import os


def ensure_folder_structure(addon_path):
    os.makedirs(addon_path, exist_ok=True)
    os.makedirs(os.path.join(addon_path, "addon"), exist_ok=True)
    os.makedirs(os.path.join(addon_path, "assets"), exist_ok=True)
