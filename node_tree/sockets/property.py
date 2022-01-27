import bpy
from .base_socket import ScriptingSocket
from .property_template import PropertySocket



blend_data_defaults = {
    "Scene": {
        "value": "(bpy.context, 'scene')",
        "name": "Using Active"},
    "Object": {
        "value": "(bpy.context, 'active_object')",
        "name": "Using Active"},
    "Preferences": {
        "value": "(self, '')",
        "name": "Using Self"},
    "Operator": {
        "value": "(self, '')",
        "name": "Using Self"},
}



class SN_PropertySocket(bpy.types.NodeSocket, ScriptingSocket, PropertySocket):

    bl_idname = "SN_PropertySocket"
    group = "DATA"
    bl_label = "Property"


    @property
    def default_python_value(self):
        if self.name in blend_data_defaults:
            return blend_data_defaults[self.name]["value"]
        return "(None, 'NONE')"
    
    default_prop_value = (None, "NONE")

    def get_python_repr(self):
        return self.default_python_value # python_value of this socket should be set as (property_source, 'property_name', indexing{optional})
    
    
    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    

    def get_color(self, context, node):
        return (0, 0.87, 0.7)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output and not self.is_linked:
            if self.name in blend_data_defaults:
                text += f" ({blend_data_defaults[self.name]['name']})"
            else:
                text += " (NO VALUE!)"
        layout.label(text=text)