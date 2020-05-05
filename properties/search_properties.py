import bpy


class SN_SearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier",default="")
    description: bpy.props.StringProperty(name="Description",default="")


bpy.utils.register_class(SN_SearchPropertyGroup)
bpy.types.Scene.sn_op_type_properties = bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
bpy.types.Scene.sn_op_run_properties = bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)