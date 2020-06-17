import bpy


class SN_SearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier",default="")
    description: bpy.props.StringProperty(name="Description",default="")
    type: bpy.props.StringProperty(name="Type",default="")
