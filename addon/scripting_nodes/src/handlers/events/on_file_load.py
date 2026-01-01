from scripting_nodes.src.handlers.msgbus.node_tree_name import subscribe_to_name_change
from names_generator import generate_name
from scripting_nodes.src.features.node_tree.code_gen.modules.persisted import (
    get_modules_to_persist,
)
from scripting_nodes.src.lib.constants.paths import DEV_ADDON_MODULE
from scripting_nodes.src.features.node_tree.code_gen.modules.modules import (
    unregister_module,
)
from scripting_nodes.src.features.node_tree.code_gen.file_management.clear_addon import (
    clear_module_files,
)
from scripting_nodes.src.handlers.timers.node_tree_watcher import (
    register_node_tree_watcher,
)
import addon_utils
import bpy
from bpy.app.handlers import persistent


@persistent
def on_file_load_pre(dummy):
    unregister_module(DEV_ADDON_MODULE)
    clear_module_files(DEV_ADDON_MODULE)


@persistent
def on_file_load_post(dummy):
    subscribe_to_name_change()

    bpy.context.scene.sna.addon.is_dirty = True

    # update name
    if bpy.context.scene.sna.addon.addon_name == "My Addon":
        bpy.context.scene.sna.addon.addon_name = (
            generate_name(style="capital") + " Addon"
        )

    # reload all persisted modules
    for module in get_modules_to_persist():
        if module == bpy.context.scene.sna.addon.module_name:
            unregister_module(module)
        else:
            addon_utils.enable(module, default_set=True, persistent=True)

    # watch changes
    register_node_tree_watcher()


def register():
    bpy.app.handlers.load_pre.append(on_file_load_pre)
    bpy.app.handlers.load_post.append(on_file_load_post)


def unregister():
    bpy.app.handlers.load_pre.remove(on_file_load_pre)
    bpy.app.handlers.load_post.remove(on_file_load_post)
