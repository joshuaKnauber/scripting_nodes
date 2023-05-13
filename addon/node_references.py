import bpy


class SN_NodeReference(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")

    id: bpy.props.StringProperty(name="ID", default="")
