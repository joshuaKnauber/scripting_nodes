import shutil
import os
from scripting_nodes.src.lib.constants.paths import ADDON_FOLDER


def clear_addon_files(addon_path):
    if os.path.exists(addon_path):
        shutil.rmtree(addon_path)


def clear_module_files(module_name):
    path = os.path.join(ADDON_FOLDER, module_name)
    clear_addon_files(path)
