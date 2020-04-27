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


class SN_NumberSocket(bpy.types.NodeSocket):
    '''Number Socket for handeling integers'''
    bl_idname = 'SN_NumberSocket'
    bl_label = "Number"

    number_value: bpy.props.FloatProperty(
        name="Number",
        description="Socket for a number value",
        default=0,
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text="Value")
        else:
            layout.prop(self, "number_value", text=text)

    def draw_color(self, context, node):
        return socket_colors["NUMBER"]
