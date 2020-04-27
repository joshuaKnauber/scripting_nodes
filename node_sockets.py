import bpy
from .nodes.node_looks import socket_colors


class SN_StringSocket(bpy.types.NodeSocket):
    '''String Socket for handling text'''
    bl_idname = 'SN_StringSocket'
    bl_label = "String"

    string_value: bpy.props.StringProperty(
        name="String",
        description="Socket for a string value",
        default="",
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=self.string_value)
        else:
            layout.prop(self, "string_value", text=text)

    def draw_color(self, context, node):
        return socket_colors["STRING"]
