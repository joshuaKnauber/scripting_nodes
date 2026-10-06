import bpy
from bpy.app.handlers import persistent

from ...core import scheduler


@persistent
def on_save_pre(dummy):
    # Make sure the files on disk match what is being saved
    scheduler.flush()


def register():
    bpy.app.handlers.save_pre.append(on_save_pre)


def unregister():
    bpy.app.handlers.save_pre.remove(on_save_pre)
