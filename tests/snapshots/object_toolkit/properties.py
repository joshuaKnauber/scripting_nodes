import bpy

from .logic import on_spacing_update


class OBJECT_TOOLKIT_PG_selection_set(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Set")
    objects: bpy.props.StringProperty(name="Objects")


class OBJECT_TOOLKIT_PG_scene_properties(bpy.types.PropertyGroup):
    spacing: bpy.props.FloatProperty(
        name="Spacing", default=2.0, unit="LENGTH", update=on_spacing_update
    )
    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
        ],
    )
    sets: bpy.props.CollectionProperty(
        name="Sets", type=OBJECT_TOOLKIT_PG_selection_set
    )
    active_set: bpy.props.IntProperty(name="Active Set")


def register():
    bpy.types.Scene.object_toolkit = bpy.props.PointerProperty(
        type=OBJECT_TOOLKIT_PG_scene_properties
    )


def unregister():
    del bpy.types.Scene.object_toolkit
