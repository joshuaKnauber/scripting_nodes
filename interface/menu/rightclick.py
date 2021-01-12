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
    
    full_path: bpy.props.StringProperty(options={"HIDDEN"})
    identifier: bpy.props.StringProperty(options={"HIDDEN"})
    name: bpy.props.StringProperty(options={"HIDDEN"})
    data_type: bpy.props.StringProperty(options={"HIDDEN"})
    
    
    def copy(self,data):
        bpy.context.window_manager.clipboard = data
    
        
    def construct(self, data_block_identifier, data_block_type, data_block_name):
        data = {
            "data_block": {
                "type": data_block_type,
                "name": data_block_name,
                "identifier": data_block_identifier
            },
            "full_path": self.full_path,
            "identifier": self.identifier,
            "name": self.name,
            "type": self.data_type
        }
        return json.dumps(data)
    
    
    def space_data(self):
        return self.construct("bpy.context.screen.areas[\"My Area\"].spaces[0]", "SpaceData", "Area")


    def preferences(self):
        suffix = ""
        return self.construct("bpy.context.preferences" + suffix)

        
    def default(self):
        db_path = self.full_path.split("[")[:-1]
        db_path = "[".join(db_path)
        db_as_prop_path = ".".join(db_path.split(".")[:-1])
        data_block = eval(f"{db_as_prop_path}.bl_rna.properties[\"{db_path.split('.')[-1]}\"]")
        return self.construct(db_path.split(".")[-1], data_block.fixed_type.identifier, data_block.fixed_type.name)


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
            
        op.full_path = property_pointer.__repr__()
        op.identifier = property_value.identifier
        op.name = property_value.name
        op.data_type = property_value.type
            
    if button_value:
        layout.operator("ui.copy_python_command_button",text="Serpens | Copy Operator",icon="COPYDOWN")