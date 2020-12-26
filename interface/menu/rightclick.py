import bpy



class SN_OT_CopyProperty(bpy.types.Operator):
    bl_idname = "sn.copy_space_property"
    bl_label = "Copy Space Property"
    bl_description = "Copy the property from this space"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    identifier: bpy.props.StringProperty(options={"HIDDEN"})

    def execute(self, context):
        bpy.context.window_manager.clipboard = "bpy.context.screen.areas['area'].spaces[0]."+self.identifier
        return {"FINISHED"}




class WM_MT_button_context(bpy.types.Menu):
    bl_label = "Unused"

    def draw(self, context):
        pass


def serpens_right_click(self, context):
    layout = self.layout

    property_value = getattr(context, "button_prop", None)
    button_value = getattr(context, "button_operator", None)    
    show_copy = bpy.ops.ui.copy_data_path_button.poll()

    if show_copy or property_value or button_value:
        layout.separator()
    
    if show_copy:
        layout.operator("ui.copy_data_path_button",text="Serpens | Copy Property",icon="COPYDOWN").full_path = True
    elif property_value:
        layout.operator("sn.copy_space_property",text="Serpens | Copy Property",icon="COPYDOWN").identifier = property_value.identifier
    
    if button_value:
        layout.operator("ui.copy_python_command_button",text="Serpens | Copy Button",icon="COPYDOWN")