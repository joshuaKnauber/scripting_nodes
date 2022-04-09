import bpy
from .base_socket import ScriptingSocket



class SN_ListSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_ListSocket"
    group = "DATA"
    bl_label = "List"
    socket_shape = "SQUARE"


    default_python_value = "[]"
    default_prop_value = []

    def get_python_repr(self):
        return f"[]"

    default_value: bpy.props.StringProperty(name="Value",
                                            default="",
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)

    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    

    def get_color(self, context, node):
        return (0.85, 0.15, 1)

    def draw_socket(self, context, layout, node, text, minimal=False):
        layout.label(text=text)