import shutil
import os
from scripting_nodes.src.lib.constants.paths import DEV_ADDON_PATH, PROD_ADDON_PATH
import bpy


def clear_addon_files(addon_path):
    if os.path.exists(addon_path):
        shutil.rmtree(addon_path)


def clear_last_build():
    if bpy.context.scene.sna.addon.force_production:
        clear_addon_files(PROD_ADDON_PATH())
    else:
        clear_addon_files(DEV_ADDON_PATH)
