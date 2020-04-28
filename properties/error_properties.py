import bpy


class SN_ErrorPropertyGroup(bpy.types.PropertyGroup):

    error_type: bpy.props.StringProperty(name="Error type", default="")
    error_message: bpy.props.StringProperty(name="Error message", default="")
    fatal_error: bpy.props.BoolProperty(name="Fatal error", default=False)
    node: bpy.props.StringProperty(name="Node",default="")


bpy.utils.register_class(SN_ErrorPropertyGroup)
bpy.types.Scene.sn_error_properties = bpy.props.CollectionProperty(type=SN_ErrorPropertyGroup)
