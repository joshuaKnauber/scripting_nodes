from ...lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
)
import bpy
from bpy.app.handlers import persistent


@persistent
def on_depsgraph_update(dummy):
    for ntree in scripting_node_trees():
        if not ntree.initialized:
            ntree.init()


def register():
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)


def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
