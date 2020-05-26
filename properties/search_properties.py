import bpy


class SN_SearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier",default="")
    description: bpy.props.StringProperty(name="Description",default="")
    isCustom: bpy.props.BoolProperty(name="Operator is custom",default=False)
    propType: bpy.props.StringProperty(name="Type of property",default="")


bpy.utils.register_class(SN_SearchPropertyGroup)
bpy.types.Scene.sn_op_type_properties = bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
bpy.types.Scene.sn_op_run_properties = bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
bpy.types.Scene.sn_panel_properties = bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
bpy.types.Scene.sn_space_properties = bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
bpy.types.Scene.sn_region_properties = bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
bpy.types.Scene.sn_context_properties = bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
bpy.types.Scene.sn_category_properties = bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)