from scripting_nodes.src.features.node_tree.code_gen.modules.to_remove import (
    clear_modules_to_remove,
    get_modules_to_remove,
)
from scripting_nodes.src.features.node_tree.code_gen.modules.modules import (
    unregister_module,
)
from scripting_nodes.src.features.node_tree.code_gen.file_management.clear_addon import (
    clear_module_files,
)
from scripting_nodes.src.handlers.timers.node_tree_watcher import (
    register_node_tree_watcher,
)
import bpy


@bpy.app.handlers.persistent
def on_file_load_pre(dummy):
    for module in get_modules_to_remove():
        unregister_module(module)
        clear_module_files(module)
    clear_modules_to_remove()


@bpy.app.handlers.persistent
def on_file_load_post(dummy):
    bpy.context.scene.sna.addon.is_dirty = True
    register_node_tree_watcher()


def register():
    bpy.app.handlers.load_pre.append(on_file_load_pre)
    bpy.app.handlers.load_post.append(on_file_load_post)
