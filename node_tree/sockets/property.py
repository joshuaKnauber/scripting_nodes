import bpy
from .base_socket import ScriptingSocket
from ...settings.data_properties import bpy_to_path_sections



blend_data_defaults = {
    "Scenes": {
        "value": "bpy.context.scene",
        "name": "Using Active"},
    "Objects": {
        "value": "bpy.context.active_object",
        "name": "Using Active"},
        
    "Preferences": {
        "value": "self",
        "name": "Using Self"},
    "Operator": {
        "value": "self",
        "name": "Using Self"},
}



class SN_PropertySocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_PropertySocket"
    group = "DATA"
    bl_label = "Property"


    @property
    def default_python_value(self):
        if self.name in blend_data_defaults:
            return blend_data_defaults[self.name]["value"]
        return "None"
    
    default_prop_value = ""

    def get_python_repr(self):
        return self.default_python_value
    
    
    @property
    def python_attr(self):
        value = self.python_value
        if "." in value:
            return value.split(".")[-1]
        return value
    
    @property
    def python_source(self):
        value = self.python_value
        if "." in value:
            return ".".join(value.split(".")[:-1])
        return value
    
    @property
    def python_sections(self):
        sections = bpy_to_path_sections(self.python_value)
        if sections:
            return ["bpy"] + sections
        return []
    
    
    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    

    def get_color(self, context, node):
        return (0, 0.87, 0.7)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output and not self.is_linked:
            if self.name in blend_data_defaults:
                text += f" ({blend_data_defaults[self.name]['name']})"
            else:
                text += " (No Data)"
        layout.label(text=text)