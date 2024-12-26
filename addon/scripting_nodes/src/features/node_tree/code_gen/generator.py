from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
)
from .file_management.folder_structure import create_folder_structure
from .file_management.clear_addon import clear_addon_files
from .file_management.default_files import create_default_files
from scripting_nodes.src.lib.constants.paths import DEV_ADDON_PATH
from .file_management.node_tree_files import create_node_tree_file
from .generators.node_tree import code_gen_node_tree
import os


def generate_addon():
    if not has_addon():
        return

    addon_path = DEV_ADDON_PATH

    # clear existing files
    clear_addon_files(addon_path)

    # create folder structure
    create_folder_structure(addon_path)

    # create default files
    create_default_files(addon_path)

    # create node tree files
    node_tree_folder_path = os.path.join(addon_path, "addon")
    for ntree in scripting_node_trees():
        ntree_code = code_gen_node_tree(ntree)
        create_node_tree_file(node_tree_folder_path, ntree.name, ntree_code)


def has_addon():
    return len(scripting_node_trees()) > 0
