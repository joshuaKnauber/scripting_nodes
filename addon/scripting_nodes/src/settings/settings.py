from .ui_state import SNA_UISettings
from .dev import SNA_DevSettings
from .addon import SNA_AddonSettings
from ..core.properties import CATEGORIES, SNA_PropertyRef, picker_attr
import bpy


class SNA_Settings(bpy.types.PropertyGroup):
    addon: bpy.props.PointerProperty(type=SNA_AddonSettings)

    dev: bpy.props.PointerProperty(type=SNA_DevSettings)

    ui: bpy.props.PointerProperty(type=SNA_UISettings)


# Property pickers, one per value type (core/properties.py)
for _category in CATEGORIES:
    SNA_Settings.__annotations__[picker_attr(_category)] = bpy.props.CollectionProperty(
        type=SNA_PropertyRef
    )


def register():
    bpy.types.Scene.sna = bpy.props.PointerProperty(type=SNA_Settings)


def unregister():
    del bpy.types.Scene.sna
