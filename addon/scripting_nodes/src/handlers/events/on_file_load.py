import bpy
from bpy.app.handlers import persistent

from ...core import runtime, scheduler
from ...lib.names import random_addon_name
from ..msgbus.node_tree_name import subscribe_to_name_change


@persistent
def on_file_load_pre(dummy):
    """Unload this file's addon before another file replaces it."""
    scene = bpy.context.scene
    if scene is None or not hasattr(scene, "sna") or not scene.sna.addon.persist_addon:
        runtime.unload_current()


@persistent
def on_file_load_post(dummy):
    subscribe_to_name_change()
    runtime.enable_persisted()
    addon = bpy.context.scene.sna.addon
    if addon.addon_name == "My Addon":
        addon.addon_name = random_addon_name()
    scheduler.request_full()


def register():
    bpy.app.handlers.load_pre.append(on_file_load_pre)
    bpy.app.handlers.load_post.append(on_file_load_post)


def unregister():
    bpy.app.handlers.load_pre.remove(on_file_load_pre)
    bpy.app.handlers.load_post.remove(on_file_load_post)
