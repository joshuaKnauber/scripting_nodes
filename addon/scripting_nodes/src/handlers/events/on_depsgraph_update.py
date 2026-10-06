import bpy
from bpy.app.handlers import persistent

from ...core import integrity, scheduler
from ...lib.trees import scripting_node_trees


@persistent
def on_depsgraph_update(dummy):
    # Trees created with Blender's "New" button or duplicated/appended need an
    # integrity pass (init, unique ids). Only a cheap check runs here.
    if integrity.has_duplicate_ids(scripting_node_trees()):
        scheduler.request_full()


def register():
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)


def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
