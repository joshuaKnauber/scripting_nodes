import os


def create_folder_structure(addon_path):
    os.makedirs(addon_path)
    os.makedirs(os.path.join(addon_path, "addon"))
    os.makedirs(os.path.join(addon_path, "assets"))
