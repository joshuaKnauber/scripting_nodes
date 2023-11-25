import bpy
from bpy.app.handlers import persistent

from .addon.info.info_properties import reset_addon_info_has_changes
from .core.builder import builder, watcher
from .interface.overlays.errors.error_drawing import draw_errors
from .interface.overlays.nodes.node_overlays import draw_node_overlays
from .msgbus import subscribe_to_name_change


def register():
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)


def unregister():
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)
    bpy.types.SpaceNodeEditor.draw_handler_remove(draw_errors, "WINDOW")
    bpy.types.SpaceNodeEditor.draw_handler_remove(draw_node_overlays, "WINDOW")


@persistent
def load_handler(dummy):
    subscribe_to_name_change()
    reset_addon_info_has_changes()
    builder.build_addon()
    # TODO do properly
    bpy.types.SpaceNodeEditor.draw_handler_add(draw_errors, (), "WINDOW", "POST_PIXEL")
    bpy.types.SpaceNodeEditor.draw_handler_add(
        draw_node_overlays, (), "WINDOW", "POST_PIXEL"
    )

    if not bpy.app.timers.is_registered(watcher.watch_addon):  # TODO unregister?
        bpy.app.timers.register(watcher.watch_addon, first_interval=0.1)


@persistent
def depsgraph_handler(dummy):
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn_tree", False):
            if not ntree.id:
                ntree._init()
