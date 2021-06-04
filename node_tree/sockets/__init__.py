import bpy


from . import base_sockets, blend_data, boolean, data, execute, float, icon, integer, interface, list, string, variable


classes = [base_sockets.SN_OT_RemoveSocket,
            base_sockets.SN_OT_AddSocket,
            blend_data.SN_BlendDataSocket,
            boolean.SN_BooleanSocket,
            boolean.SN_DynamicBooleanSocket,
            data.SN_DataSocket,
            data.SN_DynamicDataSocket,
            execute.SN_ExecuteSocket,
            execute.SN_DynamicExecuteSocket,
            float.SN_FloatSocket,
            float.SN_DynamicFloatSocket,
            icon.SN_IconSocket,
            integer.SN_IntegerSocket,
            integer.SN_DynamicIntegerSocket,
            interface.SN_InterfaceSocket,
            interface.SN_DynamicInterfaceSocket,
            list.SN_ListSocket,
            list.SN_DynamicListSocket,
            string.SN_StringSocket,
            string.SN_DynamicStringSocket,
            variable.SN_DynamicVariableSocket]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)