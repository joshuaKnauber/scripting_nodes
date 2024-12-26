from scripting_nodes.src.lib.utils.logger import log_if
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import (
    has_addon,
    scripting_node_trees,
)
from .file_management.folder_structure import ensure_folder_structure
from .file_management.clear_addon import clear_addon_files
from .file_management.default_files import ensure_default_files
from scripting_nodes.src.lib.constants.paths import DEV_ADDON_PATH, PROD_ADDON_PATH
from .file_management.node_tree_files import (
    create_node_tree_file,
    get_node_tree_file_path,
)
from .generators.node_tree import code_gen_node_tree
import os
import bpy


def generate_addon(dev=True):
    addon_path = DEV_ADDON_PATH if dev else PROD_ADDON_PATH()

    # remove addon files if no addon exists
    if not has_addon():
        clear_addon_files(addon_path)
        return

    # clear addon files if dirty
    if bpy.context.scene.sna.addon.is_dirty:
        clear_addon_files(addon_path)
        bpy.context.scene.sna.addon.is_dirty = False

    # ensure folder structure
    ensure_folder_structure(addon_path)

    # ensure default files
    ensure_default_files(addon_path)

    # update node tree files
    node_tree_folder_path = os.path.join(addon_path, "addon")
    for ntree in scripting_node_trees():
        if ntree.is_dirty or not os.path.exists(
            get_node_tree_file_path(node_tree_folder_path, ntree.name)
        ):
            log_if(
                bpy.context.scene.sna.dev.log_tree_rebuilds,
                "INFO",
                f"Rebuilding {ntree.name}",
            )
            ntree_code = code_gen_node_tree(ntree)
            create_node_tree_file(node_tree_folder_path, ntree.name, ntree_code)
            ntree.is_dirty = False
