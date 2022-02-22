import bpy



# TODO: find better solution for registering something in a rightclick menu
class WM_MT_button_context(bpy.types.Menu):
    bl_label = "Unused"
    def draw(self, context):
        pass



def serpens_right_click(self, context):
    layout = self.layout

    property_pointer = getattr(context, "button_pointer", None)
    property_value = getattr(context, "button_prop", None)
    button_value = getattr(context, "button_operator", None)    

    if property_value or button_value:
        layout.separator()
        
    if property_value and property_pointer:
        layout.operator("sn.copy_property", text="Get Serpens Property", icon="FILE_SCRIPT")
            
    if button_value:
        layout.operator("sn.copy_operator", text="Get Serpens Operator", icon="FILE_SCRIPT")
    
    if context:
        layout.operator("sn.copy_context", text="Copy Context", icon="COPYDOWN")