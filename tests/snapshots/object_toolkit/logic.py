import bpy
from bpy.app.handlers import persistent

from ._sn_helpers import sn_redraw


@persistent
def on_load_pre(*args):
    print(f"Object Toolkit: loaded {bpy.data.filepath}")


def on_spacing_update(self, context):
    sn_redraw("VIEW_3D")


def register():
    bpy.app.handlers.load_pre.append(on_load_pre)


def unregister():
    bpy.app.handlers.load_pre.remove(on_load_pre)
