import bpy


from . import create_properties, create_variables, variables_ui_list


classes = [create_properties.SN_OT_CreateProperty,
            create_properties.SN_OT_RemoveProperty,
            create_properties.SN_OT_AddPropertyGetter,
            create_properties.SN_OT_AddPropertySetter,
            create_properties.SN_OT_MoveProperty,
            create_properties.SN_OT_AddEnumItem,
            create_properties.SN_OT_RemoveEnumItem,
            create_properties.SN_OT_MoveEnumItem,
            create_variables.SN_OT_CreateVariable,
            create_variables.SN_OT_RemoveVariable,
            create_variables.SN_OT_MoveVariable,
            create_variables.SN_OT_AddVariableGetter,
            create_variables.SN_OT_AddVariableSetter,
            variables_ui_list.SN_EnumItem,
            variables_ui_list.SN_Variable,
            variables_ui_list.SN_UL_VariableList]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)