import bpy
import json

#TODO options for properties especially in operators

class SN_OT_CopyProperty(bpy.types.Operator):
    bl_idname = "sn.copy_space_property"
    bl_label = "Copy Space Property"
    bl_description = "Copy the property from this space"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    origin: bpy.props.EnumProperty(items=[("DEFAULT","DEFAULT","DEFAULT"),
                                          ("SPACE_DATA","SPACE_DATA","SPACE_DATA"),
                                          ("PREFERENCES","PREFERENCES","PREFERENCES")],
                                   options={"HIDDEN"})
    
    path: bpy.props.StringProperty(options={"HIDDEN"})
    identifier: bpy.props.StringProperty(options={"HIDDEN"})
    
    
    def copy(self,data):
        bpy.context.window_manager.clipboard = data
    
        
    def construct(self,data_block_type,data_block_path,identifier):
        data = {
            "data_block": {
                "type": data_block_type,
                "path": data_block_path
            },
            
            "identifier": identifier
        }
        return json.dumps(data)
    
    
    def space_data(self):
        return self.construct(self.path,self.identifier)


    def preferences(self):
        return self.construct(self.path,self.identifier)

        
    def default(self):
        return self.construct(self.path,self.identifier)


    def execute(self, context):
        if self.origin == "SPACE_DATA":
            self.copy(self.space_data())
        elif self.origin == "PREFERENCES":
            self.copy(self.preferences())
        elif self.origin == "DEFAULT":
            self.copy(self.default())
        return {"FINISHED"}




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
        op = layout.operator("sn.copy_space_property",text="Serpens | Copy Property",icon="COPYDOWN")
        
        if "Preferences" in property_pointer.bl_rna.identifier:
            op.origin = "PREFERENCES"
        elif "bpy.data.screens[" in property_pointer.__repr__():
            op.origin = "SPACE_DATA"
        else:
            op.origin = "DEFAULT"
            
        op.path = property_pointer.__repr__()
        op.identifier = property_value.identifier
            
    if button_value:
        layout.operator("ui.copy_python_command_button",text="Serpens | Copy Operator",icon="COPYDOWN")