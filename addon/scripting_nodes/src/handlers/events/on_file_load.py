from scripting_nodes.src.handlers.msgbus.node_tree_name import subscribe_to_name_change
from names_generator import generate_name
from scripting_nodes.src.features.node_tree.code_gen.modules.modules import (
    unregister_module,
)
from scripting_nodes.src.features.node_tree.code_gen.modules.persisted import (
    get_persisted_modules,
    get_pending_removal,
    clear_pending_removal,
)
from scripting_nodes.src.features.node_tree.code_gen.file_management.clear_addon import (
    clear_module_files,
)
from scripting_nodes.src.lib.constants.paths import ADDON_FOLDER
from scripting_nodes.src.handlers.timers.node_tree_watcher import (
    register_node_tree_watcher,
)
import addon_utils
import bpy
import os
from bpy.app.handlers import persistent


# Store the current module name so we can unregister it before loading a new file
_current_module = None


@persistent
def on_file_load_pre(dummy):
    """Unregister the current session's addon before loading a new file."""
    global _current_module

    # Try to get the current module name before the scene is replaced
    try:
        _current_module = bpy.context.scene.sna.addon.module_name
        unregister_module(_current_module)
    except:
        pass


@persistent
def on_file_load_post(dummy):
    global _current_module
    # Clean up all modules pending removal
    for module in get_pending_removal():
        unregister_module(module)
        clear_module_files(module)
    clear_pending_removal()

    subscribe_to_name_change()

    bpy.context.scene.sna.addon.is_dirty = True

    # update name
    if bpy.context.scene.sna.addon.addon_name == "My Addon":
        bpy.context.scene.sna.addon.addon_name = (
            generate_name(style="capital") + " Addon"
        )

    # Enable all persisted modules
    for module in get_persisted_modules():
        module_init_path = os.path.join(ADDON_FOLDER, module, "__init__.py")
        if os.path.exists(module_init_path):
            addon_utils.enable(module, default_set=False, persistent=False)

    # watch changes
    register_node_tree_watcher()


def register():
    bpy.app.handlers.load_pre.append(on_file_load_pre)
    bpy.app.handlers.load_post.append(on_file_load_post)


def unregister():
    bpy.app.handlers.load_pre.remove(on_file_load_pre)
    bpy.app.handlers.load_post.remove(on_file_load_post)
