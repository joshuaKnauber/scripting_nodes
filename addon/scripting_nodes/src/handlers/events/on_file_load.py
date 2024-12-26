from scripting_nodes.src.features.node_tree.code_gen.modules.modules import (
    unregister_last_module,
)
from scripting_nodes.src.features.node_tree.code_gen.file_management.clear_addon import (
    clear_last_build,
)
from scripting_nodes.src.handlers.timers.node_tree_watcher import (
    register_node_tree_watcher,
)
import bpy


@bpy.app.handlers.persistent
def on_file_load_pre(dummy):
    unregister_last_module()
    clear_last_build()


@bpy.app.handlers.persistent
def on_file_load_past(dummy):
    register_node_tree_watcher()


def register():
    bpy.app.handlers.load_pre.append(on_file_load_pre)
    bpy.app.handlers.load_post.append(on_file_load_past)
