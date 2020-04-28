import bpy
from .nodes.node_looks import socket_colors

class SN_StringSocket(bpy.types.NodeSocket):
    '''String Socket for handling text'''
    bl_idname = 'SN_StringSocket'
    bl_label = "String"

    value: bpy.props.StringProperty(
        name="String",
        description="Socket for a string value",
        default="",
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return socket_colors["STRING"]


class SN_NumberSocket(bpy.types.NodeSocket):
    '''Number Socket for handeling integers'''
    bl_idname = 'SN_NumberSocket'
    bl_label = "Number"

    value: bpy.props.FloatProperty(
        name="Number",
        description="Socket for a number value",
        default=0,
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return socket_colors["NUMBER"]


class SN_BooleanSocket(bpy.types.NodeSocket):
    '''Boolean Socket for handeling booleans'''
    bl_idname = 'SN_BooleanSocket'
    bl_label = "Boolean"

    value: bpy.props.BoolProperty(
        name="Boolean",
        description="Socket for a boolean value",
        default=False,
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=str(self.value), toggle=True)

    def draw_color(self, context, node):
        return socket_colors["BOOLEAN"]


class SN_VectorSocket(bpy.types.NodeSocket):
    '''Vector Socket for handeling vectors'''
    bl_idname = 'SN_VectorSocket'
    bl_label = "Vector"

    value: bpy.props.FloatVectorProperty(
        name="Vector",
        description="Socket for a vector value",
        default=(0,0,0),
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            col = layout.column()
            col.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return socket_colors["VECTOR"]


class SN_LayoutSocket(bpy.types.NodeSocket):
    '''Layout Socket for connecting layouts'''
    bl_idname = 'SN_LayoutSocket'
    bl_label = "Layout"

    def draw(self, context, layout, node, text):
        layout.label(text="Layout")

    def draw_color(self, context, node):
        return socket_colors["LAYOUT"]


class SN_ProgramSocket(bpy.types.NodeSocket):
    '''Program Socket for connecting nodes in the order they should be executed'''
    bl_idname = 'SN_ProgramSocket'
    bl_label = "Program"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return socket_colors["PROGRAM"]