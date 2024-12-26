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


def PROD_ADDON_PATH():
    return os.path.join(
        ADDON_FOLDER,
        bpy.context.scene.sna.addon.module_name,
    )
