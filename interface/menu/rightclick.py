import bpy
import json

#TODO options for properties especially in operators


def construct_from_property(path,prop):
    size = -1
    if prop.is_vector:
        size = prop.vector_size
    data = {
        "data_block": {
            "name": "",
            "type": ""
        },
        "group_path": path,
        "property": {
            "name": prop.name,
            "identifier": prop.identifier,
            "type": prop.var_type,
            "subtype": prop.property_subtype,
            "size": size
        }
    }
    return json.dumps(data)
    

    
def copy_from_property(path,prop):
    bpy.context.window_manager.clipboard = construct_from_property(path,prop)



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
    
    db_name: bpy.props.StringProperty(options={"HIDDEN"})
    db_type: bpy.props.StringProperty(options={"HIDDEN"})

    prop_name: bpy.props.StringProperty(options={"HIDDEN"})
    prop_identifier: bpy.props.StringProperty(options={"HIDDEN"})
    prop_type: bpy.props.StringProperty(options={"HIDDEN"})
    prop_subtype: bpy.props.StringProperty(options={"HIDDEN"})
    prop_size: bpy.props.IntProperty(options={"HIDDEN"})
    
    
    def copy(self,data):
        bpy.context.window_manager.clipboard = data
    
        
    def construct(self, db_name, db_type, group_path):
        data = {
            "data_block": {
                "name": db_name,
                "type": db_type
            },
            "group_path": group_path,
            "property": {
                "name": self.prop_name,
                "identifier": self.prop_identifier,
                "type": self.prop_type,
                "subtype": self.prop_subtype,
                "size": self.prop_size
            }
        }
        return json.dumps(data)
    
    
    def space_data(self):
        group_path = "spaces[0]" + self.full_path.split("]")[-1]
        return self.construct("Area","Area",group_path)


    def preferences(self):
        return self.construct(self.db_name + " Preferences",self.db_type,"")
                        
        
    def default(self):
        db_type = self.db_type
        db_name = self.db_name
        group_path = self.full_path.split("]")[-1][1:]
        if not self.full_path[-1] == "]":
            db = eval("]".join(self.full_path.split("]")[:-1])+"]")
            db_name = db.name
            db_type = db.bl_rna.identifier
        return self.construct(db_name,db_type,group_path)


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
        
        op.prop_name = property_value.name
        op.prop_identifier = property_value.identifier
        op.prop_type = property_value.type
        op.prop_subtype = property_value.subtype
        if hasattr(property_value,"array_length"):
            op.prop_size = property_value.array_length
        else:
            op.prop_size = -1        
        
        op.db_type = property_pointer.bl_rna.identifier
        if hasattr(property_pointer,"name"):
            op.db_name = property_pointer.name
        elif hasattr(property_pointer.bl_rna,"name"):
            op.db_name = property_pointer.bl_rna.name
            
    if button_value:
        layout.operator("ui.copy_python_command_button",text="Serpens | Copy Operator",icon="COPYDOWN")