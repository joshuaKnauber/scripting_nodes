import shutil
import os


def clear_addon_files(addon_path):
    if os.path.exists(addon_path):
        shutil.rmtree(addon_path)
