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
    bpy.app.handlers.load_post.append(load_post_handler)
    bpy.app.handlers.load_pre.append(load_pre_handler)
    bpy.app.handlers.save_post.append(save_post_handler)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)


def unregister():
    bpy.app.handlers.load_post.remove(load_post_handler)
    bpy.app.handlers.load_pre.remove(load_pre_handler)
    bpy.app.handlers.save_post.remove(save_post_handler)
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)
    try:
        bpy.types.SpaceNodeEditor.draw_handler_remove(draw_errors, "WINDOW")
    except:
        pass
    try:
        bpy.types.SpaceNodeEditor.draw_handler_remove(draw_node_overlays, "WINDOW")
    except:
        pass


@persistent
def save_post_handler(dummy):
    sn = bpy.context.scene.sna
    if builder.LAST_PROD_MODULE != builder.module(prod_name=True):
        builder.remove_addon(module=builder.LAST_PROD_MODULE)
    if sn.info.persist_sessions:
        builder.build_addon(prod_build=True, module=builder.module(prod_name=True))
        builder.disable_module(builder.module(prod_name=True))
        builder.build_addon(prod_build=sn.production_build, module=builder.dev_module())
    else:
        builder.remove_addon(module=builder.module(prod_name=True))


def on_exit():
    builder.remove_addon(module=builder.dev_module())


atexit.register(on_exit)


@persistent
def load_pre_handler(dummy):
    builder.remove_addon(module=builder.dev_module())
    builder.set_last_prod_module(module=None)


@persistent
def load_post_handler(dummy):
    sn = bpy.context.scene.sna
    initialize_addon_info()
    subscribe_to_name_change()
    reset_addon_info_has_changes()
    builder.build_addon(module=builder.dev_module(), prod_build=sn.production_build)
    builder.toggle_stored_prod_modules()
    builder.set_last_prod_module(module=builder.module(prod_name=True))
    bpy.types.SpaceNodeEditor.draw_handler_add(draw_errors, (), "WINDOW", "POST_PIXEL")
    bpy.types.SpaceNodeEditor.draw_handler_add(
        draw_node_overlays, (), "WINDOW", "POST_PIXEL"
    )
    if not bpy.app.timers.is_registered(watcher.watch_addon):
        bpy.app.timers.register(watcher.watch_addon, first_interval=0.1)


@persistent
def depsgraph_handler(dummy):
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn_ntree", False):
            if not ntree.id:
                ntree._init()
