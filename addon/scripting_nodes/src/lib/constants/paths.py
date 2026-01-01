import os
import bpy

NODES_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "features",
    "nodes",
    "categories",
)


# For extensions, we need to put generated addons in Blender's scripts/addons folder
# not inside the extension directory
def _get_addon_folder():
    """Get the folder where generated addons should be placed."""
    # Use Blender's user scripts/addons path for generated addons
    user_scripts = bpy.utils.user_resource("SCRIPTS", path="addons", create=True)
    return user_scripts


ADDON_FOLDER = _get_addon_folder()

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
