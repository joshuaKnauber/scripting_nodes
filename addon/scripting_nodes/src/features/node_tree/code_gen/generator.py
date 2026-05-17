from ....lib.utils.logger import fmt_duration, log_if
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
import time
import bpy


def generate_addon(base_path=ADDON_FOLDER):
    """Generate the addon files for the current module.

    Returns (changed_tree_modules, needs_full_reload):
      - changed_tree_modules: set of tree module names whose .py was rewritten
      - needs_full_reload: True if the change requires a full addon reload
        (default files changed, is_dirty wipe, stale tree files removed, etc.)
    """
    addon_path = get_addon_path(base_path=base_path)
    changed_trees = set()
    needs_full_reload = False

    # remove addon files if no addon exists
    if not has_addon():
        clear_addon_files(addon_path)
        return changed_trees, True

    # clear addon files if dirty - full wipe means we need full reload
    if bpy.context.scene.sna.addon.is_dirty:
        clear_addon_files(addon_path)
        bpy.context.scene.sna.addon.is_dirty = False
        needs_full_reload = True

    # ensure folder structure
    ensure_folder_structure(addon_path)

    # ensure default files - if they changed (e.g. first creation, settings
    # update later), the addon's top-level __init__ / manifest need full reload
    if ensure_default_files(addon_path):
        needs_full_reload = True

    # update node tree files
    log_rebuilds = bpy.context.scene.sna.dev.log_tree_rebuilds
    node_tree_folder_path = os.path.join(addon_path, "addon")
    stale_ntree_files = set(os.listdir(node_tree_folder_path)) - {"__init__.py"}
    for ntree in scripting_node_trees():
        stale_ntree_files.discard(ntree.module_name + ".py")
        if ntree.is_dirty or not os.path.exists(
            get_node_tree_file_path(node_tree_folder_path, ntree.module_name)
        ):
            t_start = time.perf_counter()
            ntree_code = code_gen_node_tree(ntree)
            gen_time = time.perf_counter() - t_start
            file_written = create_node_tree_file(
                node_tree_folder_path, ntree.module_name, ntree_code
            )
            if file_written:
                changed_trees.add(ntree.module_name)
            ntree.is_dirty = False
            if log_rebuilds:
                node_count = sum(1 for _ in sn_nodes(ntree))
                status = "written" if file_written else "skipped"
                log_if(
                    True,
                    "INFO",
                    f"codegen {ntree.name}: {node_count} nodes, "
                    f"{fmt_duration(gen_time)}, {status}",
                )

    # remove deleted node tree files - removed trees mean classes need to be
    # unregistered, easiest done via full reload
    for ntree_file in stale_ntree_files:
        path = os.path.join(node_tree_folder_path, ntree_file)
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)
            needs_full_reload = True

    return changed_trees, needs_full_reload


def has_changes():
    return bpy.context.scene.sna.addon.is_dirty or any(
        [ntree.is_dirty for ntree in scripting_node_trees()]
    )
