import bpy
from .base_socket import ScriptingSocket



class SN_BlendDataSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_BlendDataSocket"
    group = "DATA"
    bl_label = "Blend Data"


    default_python_value = ""
    default_prop_value = None

    def get_python_repr(self):
        return f"None"
    
    def on_subtype_update(self):
        self.display_shape = {
            "NONE": "CIRCLE",
            "COLLECTION": "SQUARE",
        }[self.subtype]

    subtypes = ["NONE", "COLLECTION"]
    subtype_values = {"NONE": "default_value", "COLLECTION": "default_value"}
    

    def get_color(self, context, node):
        return (0, 0.87, 0.7)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)
