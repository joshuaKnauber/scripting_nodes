import bpy
from .base_socket import ScriptingSocket



class SN_IconSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_IconSocket"
    group = "DATA"
    bl_label = "Icon"


    default_python_value = "0"
    default_prop_value = 0

    def get_python_repr(self):
        value = self.default_value
        return f"{value}"


    default_value: bpy.props.IntProperty(name="Value",
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)


    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}


    def get_color(self, context, node):
        return (1,0.4,0.2)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)
        if not self.is_linked and not self.is_output:
            row = layout.row()
            row.scale_x = 1.74
            op = row.operator("sn.select_icon", text="Choose Icon", icon_value=self.default_value)
            op.node = node.name
            op.socket = self.index

