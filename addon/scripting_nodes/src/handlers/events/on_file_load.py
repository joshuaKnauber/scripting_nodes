from scripting_nodes.src.handlers.timers.node_tree_watcher import (
    register_node_tree_watcher,
)
import bpy


@bpy.app.handlers.persistent
def on_file_load(dummy):
    register_node_tree_watcher()


def register():
    bpy.app.handlers.load_post.append(on_file_load)
