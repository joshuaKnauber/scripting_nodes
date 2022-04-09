import bpy
from .base_socket import ScriptingSocket



class SN_BooleanSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_BooleanSocket"
    group = "DATA"
    bl_label = "Boolean"


    default_python_value = "False"
    default_prop_value = False

    def get_python_repr(self):
        return f"{self.default_value}"

    default_value: bpy.props.BoolProperty(name="Value",
                                            default=False,
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)

    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    

    def get_color(self, context, node):
        return (0.95, 0.73, 1)

    def draw_socket(self, context, layout, node, text, minimal=False):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, self.subtype_attr, text=text)