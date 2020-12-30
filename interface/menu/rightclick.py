import bpy
import json



class SN_OT_CopyProperty(bpy.types.Operator):
    bl_idname = "sn.copy_space_property"
    bl_label = "Copy Space Property"
    bl_description = "Copy the property from this space"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    prop_name: bpy.props.StringProperty(options={"HIDDEN"})
    prop_type: bpy.props.StringProperty(options={"HIDDEN"})
    prop_array_length: bpy.props.IntProperty(options={"HIDDEN"})
    path: bpy.props.StringProperty(options={"HIDDEN"})
    
    def process_data_part(self,part,path_progress):
        part_details = {"is_numeric":False}

        suffix = "(" + eval(path_progress + ".bl_rna.base.name") + ")"
        if suffix == "(ID)":
            suffix = ""
        
        if part.split("[")[-1].split("]")[0].isnumeric():
            suffix = ""
            part_details["is_numeric"] = True
            part_details["index"] = int(part.split("[")[-1].split("]")[0])
            
        else:
            part_details["data_type"] = "bpy.types." + eval(path_progress + ".bl_rna.name")

        part_details["name"] = eval(path_progress + ".bl_rna.name") + suffix
        return part_details

    def process_part(self,part,index,path_progress):
        if not ("[" in part and "]" in part):
            return part
        elif "areas[" in part:
            return {"is_numeric":False,"name":"Area", "data_type": "bpy.types.Area"}
        elif not "spaces[0]" in part:
            if index == len(self.path.split("."))-1:
                return part.split("[")[0]
            else:
                return self.process_data_part(part,path_progress)

    def construct_path_parts(self):
        parts = []
        path_progress = ""
        for index, part in enumerate(self.path.split(".")):
            path_progress = part if not path_progress else path_progress + "." + part
            parts.append(self.process_part(part,index,path_progress))
        return parts
    
    def area_index(self):
        for index, a in enumerate(bpy.context.screen.areas):
            if a == bpy.context.area:
                return index
        return 0
    
    def handle_screen_props(self):
        if "bpy.data.screens[" in self.path:
            new_path = ".".join(self.path.split(".")[3:])
            new_path = f"bpy.context.screen.areas[{self.area_index()}].spaces[0]."
            self.path = new_path

    def execute(self, context):
        self.handle_screen_props()
        path_details = {
            "path": self.path,
            "prop_name": self.prop_name,
            "prop_type": self.prop_type,
            "prop_array_length": self.prop_array_length,
            "path_parts": self.construct_path_parts()
        }
        bpy.context.window_manager.clipboard = json.dumps(path_details)
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
        op.prop_name = property_value.name
        op.prop_type = property_value.type
        if hasattr(property_value,"array_length"):
            op.prop_array_length = property_value.array_length
        else:
            op.prop_array_length = 0
        op.path = property_pointer.__repr__()
        op.path += "." + property_value.identifier
    
    if button_value:
        layout.operator("ui.copy_python_command_button",text="Serpens | Copy Button",icon="COPYDOWN")