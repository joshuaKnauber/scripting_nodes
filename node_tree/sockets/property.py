import bpy
from .base_socket import ScriptingSocket



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



class SN_PropertySocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_PropertySocket"
    group = "DATA"
    bl_label = "Property"


    @property
    def default_python_value(self):
        if self.name in blend_data_defaults:
            return blend_data_defaults[self.name]["value"]
        return "(None, 'NONE')"
    
    def get_python_repr(self):
        return self.default_python_value # python_value of this socket should be set as (property_source, 'property_name')

    default_prop_value = (None, "NONE")
    
    
    def _get_python_value_parts(self):
        """ Returns the value of this property socket as parts """
        value = self.python_value
        if "," in value and "(" in value and ")" in value:
            split = value.replace("(", "").replace(")", "").split(",")
            for i in range(len(split)):
                split[i] = split[i].strip()
            return split
        return [None, "NONE"]
    
    
    @property
    def python_value_pointer(self):
        """ Returns the value of this property socket not as a tuple but as its full representation """
        parts = self._get_python_value_parts()
        value = parts[0]
        if len(parts[1]) > 2: # if prop name is not empty string
            value += f".{parts[1][1:-1]}"
        if len(parts) == 3:
            value += f"[{parts[2]}]"
        return value
    
    @property
    def python_value_source(self):
        """ Returns the value of this property socket not as a tuple but only the property source """
        parts = self._get_python_value_parts()
        value = parts[0]
        return value
    
    @property
    def python_value_name(self):
        """ Returns the value of this property socket not as a tuple but only the property name """
        parts = self._get_python_value_parts()
        return parts[1]
    
    
    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    

    def get_color(self, context, node):
        return (0, 0.87, 0.7)

    def draw_socket(self, context, layout, node, text):
        if self.name in blend_data_defaults:
            text += f" ({blend_data_defaults[self.name]['name']})"
        elif not self.is_output and not self.is_linked:
            text += " (NO VALUE!)"
        layout.label(text=text)