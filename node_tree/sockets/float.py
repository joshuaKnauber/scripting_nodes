import bpy
from .base_socket import ScriptingSocket



class SN_FloatSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_FloatSocket"
    group = "DATA"
    bl_label = "Float"


    default_python_value = "0"
    default_prop_value = 0

    def get_python_repr(self):
        return f"{getattr(self, self.subtype_attr)}"

    default_value: bpy.props.FloatProperty(name="Value",
                                            default=0,
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)

    factor_value: bpy.props.FloatProperty(name="Value",
                                            default=0,
                                            description="Value of this socket",
                                            soft_min=0,
                                            soft_max=1,
                                            update=ScriptingSocket._update_value)

    subtypes = ["NONE", "FACTOR"]
    subtype_values = {"NONE": "default_value", "FACTOR": "factor_value"}
    

    def get_color(self, context, node):
        return (0.6, 0.6, 0.6)

    def draw_socket(self, context, layout, node, text, minimal=False):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, self.subtype_attr, text=text, slider=self.subtype == "FACTOR")