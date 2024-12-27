import os
import bpy

NODES_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "features",
    "nodes",
    "categories",
)

ADDON_FOLDER = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

DEV_ADDON_MODULE = "scripting_nodes_temp"

DEV_ADDON_PATH = os.path.join(
    ADDON_FOLDER,
    DEV_ADDON_MODULE,
)


def PROD_ADDON_PATH(module_name=None, base_path=ADDON_FOLDER):
    if module_name is None:
        module_name = bpy.context.scene.sna.addon.module_name
    return os.path.join(
        base_path,
        module_name,
    )
