import bpy
from bpy.app.handlers import persistent
from .properties.files.load_files import load_files


def register():
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    bpy.app.handlers.load_post.remove(load_handler)


@persistent
def load_handler(dummy):
    sn = bpy.context.scene.sn
    if not sn:
        return
    # load_files(sn.addon_location)
