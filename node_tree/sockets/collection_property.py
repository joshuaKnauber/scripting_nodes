import bpy
from .base_socket import ScriptingSocket
from .property_template import PropertySocket



class SN_CollectionPropertySocket(bpy.types.NodeSocket, ScriptingSocket, PropertySocket):

    bl_idname = "SN_CollectionPropertySocket"
    group = "DATA"
    bl_label = "Collection Property"
    socket_shape = "SQUARE"


    default_python_value = "None"
    default_prop_value = ""
    
    def get_python_repr(self):
        return self.default_python_value


    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    

    def get_color(self, context, node):
        return (0, 0.87, 0.7)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)