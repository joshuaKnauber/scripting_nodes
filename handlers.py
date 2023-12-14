import bpy
from bpy.app.handlers import persistent
import atexit

from .addon.info.info_properties import (
    initialize_addon_info,
    reset_addon_info_has_changes,
)
from .core.builder import builder, watcher
from .interface.overlays.errors.error_drawing import draw_errors
from .interface.overlays.nodes.node_overlays import draw_node_overlays
from .msgbus import subscribe_to_name_change


def register():
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.load_pre.append(load_pre_handler)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)
    atexit.register(on_exit)


def unregister():
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.load_pre.remove(load_pre_handler)
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)
    try:
        bpy.types.SpaceNodeEditor.draw_handler_remove(draw_errors, "WINDOW")
    except:
        pass
    try:
        bpy.types.SpaceNodeEditor.draw_handler_remove(draw_node_overlays, "WINDOW")
    except:
        pass
    atexit.unregister(on_exit)


def on_exit():  # TODO not running
    if not builder.has_addon():
        return
    if bpy.context.scene.sna.info.persist_sessions:
        builder.build_addon(builder._get_addons_dir(), True)
    else:
        builder.remove_addon()


@persistent
def load_pre_handler(dummy):
    if not builder.has_addon():
        return
    if bpy.context.scene.sna.info.persist_sessions:
        builder.build_addon(builder._get_addons_dir(), True)
    else:
        builder.remove_addon()


@persistent
def load_handler(dummy):
    initialize_addon_info()
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
        if getattr(ntree, "is_sn_ntree", False):
            if not ntree.id:
                ntree._init()
