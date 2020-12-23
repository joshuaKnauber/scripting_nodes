import bpy



class WM_MT_button_context(bpy.types.Menu):
    bl_label = "Unused"

    def draw(self, context):
        pass


def serpens_right_click(self, context):
    layout = self.layout

    property_value = getattr(context, "button_prop", None)
    button_value = getattr(context, "button_operator", None)
            
    layout.separator()
    layout.operator("ui.copy_data_path_button",text="Serpens | Copy Property",icon="COPYDOWN").full_path = True
    layout.operator("ui.copy_python_command_button",text="Serpens | Copy Button")