from .sn_settings.dev_properties import SNA_DevSettings
from .addon_settings.addon_properties import SNA_AddonSettings
import bpy


class SNA_Settings(bpy.types.PropertyGroup):

    addon: bpy.props.PointerProperty(type=SNA_AddonSettings)

    dev: bpy.props.PointerProperty(type=SNA_DevSettings)


def register():
    bpy.types.Scene.sna = bpy.props.PointerProperty(type=SNA_Settings)


def unregister():
    del bpy.types.Scene.sna
