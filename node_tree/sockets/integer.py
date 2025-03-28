import bpy
from .base_socket import ScriptingSocket



class SN_IntegerSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_IntegerSocket"
    group = "DATA"
    bl_label = "Integer"


    default_python_value = "0"
    default_prop_value = 0

    def get_python_repr(self):
        return f"{self.default_value}"

    default_value: bpy.props.IntProperty(name="Value",
                                            default=0,
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)

    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    
    
    def get_color(self, context, node):
        return (0.15, 0.52, 0.17)

    def draw_socket(self, context, layout, node, text, minimal=False):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, self.subtype_attr, text=text)