from scripting_nodes.src.features.node_tree.code_gen.watcher import watch_changes
import bpy


def register_node_tree_watcher():
    if not bpy.app.timers.is_registered(watch_changes):
        bpy.app.timers.register(watch_changes)
