import bpy
from .base_socket import ScriptingSocket



class SN_DataSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_DataSocket"
    group = "DATA"
    bl_label = "Data"


    default_python_value = "None"
    default_prop_value = ""

    def get_python_repr(self):
        return f""
    

    def get_color(self, context, node):
        return (0.2, 0.2, 0.2)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)