import bpy
import os


def watch_files():
    sn = bpy.context.scene.sn
    if sn.use_addon and sn.use_files and os.path.exists(sn.addon_location):
        pass
