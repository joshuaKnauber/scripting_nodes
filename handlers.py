import bpy
from bpy.app.handlers import persistent

from .interface.overlays.errors.error_drawing import draw_errors
from .interface.overlays.nodes.node_overlays import draw_node_overlays
from .msgbus import subscribe_to_name_change


def register():
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.types.SpaceNodeEditor.draw_handler_remove(draw_errors, 'WINDOW')
    bpy.types.SpaceNodeEditor.draw_handler_remove(draw_node_overlays, 'WINDOW')


@persistent
def load_handler(dummy):
    sn = bpy.context.scene.sn
    subscribe_to_name_change()
    # TODO do properly
    bpy.types.SpaceNodeEditor.draw_handler_add(draw_errors, (), 'WINDOW', 'BACKDROP')
    bpy.types.SpaceNodeEditor.draw_handler_add(draw_node_overlays, (), 'WINDOW', 'BACKDROP')
