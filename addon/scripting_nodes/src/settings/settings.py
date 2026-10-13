from .ui_state import SNA_UISettings
from .dev import SNA_DevSettings
from .addon import SNA_AddonSettings
import bpy


class SNA_Settings(bpy.types.PropertyGroup):
    addon: bpy.props.PointerProperty(type=SNA_AddonSettings)

    dev: bpy.props.PointerProperty(type=SNA_DevSettings)

    ui: bpy.props.PointerProperty(type=SNA_UISettings)


def register():
    bpy.types.Scene.sna = bpy.props.PointerProperty(type=SNA_Settings)


def unregister():
    del bpy.types.Scene.sna
