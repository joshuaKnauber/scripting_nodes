import bpy
from .base_socket import ScriptingSocket



blend_data_defaults = {
    "Scene": {
        "value": "(bpy.context, 'scene')",
        "name": "Using Active"},
    "Object": {
        "value": "(bpy.context, 'active_object')",
        "name": "Using Active"},
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
            if len(split) == 2:
                for i in range(len(split)):
                    split[i] = split[i].strip()
                return split
        return [value]
    
    
    @property
    def python_value_pointer(self):
        """ Returns the value of this property socket not as a tuple but as its full representation """
        parts = self._get_python_value_parts()
        if len(parts) == 2:
            if parts[0] == "self": return "self"
            return f"{parts[0]}.{parts[1][1:-1]}"
        return self.python_value
    
    @property
    def python_value_source(self):
        """ Returns the value of this property socket not as a tuple but only the property source """
        parts = self._get_python_value_parts()
        if len(parts) == 2:
            if parts[0] == "self": return "self"
            return parts[0]
        return self.python_value
    
    @property
    def python_value_name(self):
        """ Returns the value of this property socket not as a tuple but only the property name """
        parts = self._get_python_value_parts()
        if len(parts) == 2:
            if parts[0] == "self": return "self"
            return parts[1]
        return self.python_value
    
    
    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    

    def get_color(self, context, node):
        return (0, 0.87, 0.7)

    def draw_socket(self, context, layout, node, text):
        if self.name in blend_data_defaults:
            text += f" ({blend_data_defaults[self.name]['name']})"
        elif not self.is_output and not self.is_linked:
            text += " (NO CONNECTION!)"
        layout.label(text=text)