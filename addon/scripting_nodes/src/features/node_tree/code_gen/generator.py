from ....lib.utils.logger import log_if
from ....lib.utils.node_tree.scripting_node_trees import (
    has_addon,
    scripting_node_trees,
    sn_nodes,
)
from .file_management.folder_structure import ensure_folder_structure
from .file_management.clear_addon import clear_addon_files
from .file_management.default_files import ensure_default_files
from ....lib.constants.paths import (
    ADDON_FOLDER,
    get_addon_path,
)
from .file_management.node_tree_files import (
    create_node_tree_file,
    get_node_tree_file_path,
)
from .generators.node_tree import code_gen_node_tree
import os
import bpy


def generate_addon(base_path=ADDON_FOLDER):
    """Generate the addon files for the current module."""
    addon_path = get_addon_path(base_path=base_path)
    files_changed = False

    # remove addon files if no addon exists
    if not has_addon():
        clear_addon_files(addon_path)
        return True

    # clear addon files if dirty
    if bpy.context.scene.sna.addon.is_dirty:
        clear_addon_files(addon_path)
        bpy.context.scene.sna.addon.is_dirty = False
        files_changed = True

    # ensure folder structure
    ensure_folder_structure(addon_path)

    # ensure default files
    files_changed = ensure_default_files(addon_path) or files_changed

    # regenerate nodes to match production or dev mode
    for ntree in scripting_node_trees():
        for node in sn_nodes(ntree):
            node._generate()

    # update node tree files
    node_tree_folder_path = os.path.join(addon_path, "addon")
    stale_ntree_files = set(os.listdir(node_tree_folder_path)) - {"__init__.py"}
    for ntree in scripting_node_trees():
        stale_ntree_files.discard(ntree.module_name + ".py")
        if ntree.is_dirty or not os.path.exists(
            get_node_tree_file_path(node_tree_folder_path, ntree.module_name)
        ):
            log_if(
                bpy.context.scene.sna.dev.log_tree_rebuilds,
                "INFO",
                f"Rebuilding {ntree.name}",
            )
            ntree_code = code_gen_node_tree(ntree)
            files_changed = (
                create_node_tree_file(
                    node_tree_folder_path, ntree.module_name, ntree_code
                )
                or files_changed
            )
            ntree.is_dirty = False

    # remove deleted node tree files
    for ntree_file in stale_ntree_files:
        path = os.path.join(node_tree_folder_path, ntree_file)
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)
            files_changed = True

    return files_changed


def has_changes():
    return bpy.context.scene.sna.addon.is_dirty or any(
        [ntree.is_dirty for ntree in scripting_node_trees()]
    )
