import bpy
from .node_looks import socket_colors
from ...compile.compiler import compiler

def socket_update(self, context):
    compiler().socket_update(context)

class SN_StringSocket(bpy.types.NodeSocket):
    '''String Socket for handling text'''
    bl_idname = 'SN_StringSocket'
    bl_label = "String"

    value: bpy.props.StringProperty(
        name="String",
        description="Socket for a string value",
        default="",
        update=socket_update
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return socket_colors["STRING"]


class SN_FloatSocket(bpy.types.NodeSocket):
    '''Float Socket for handeling floats'''
    bl_idname = 'SN_FloatSocket'
    bl_label = "Number"

    value: bpy.props.FloatProperty(
        name="Float",
        description="Socket for a float value",
        default=0.0,
        update=socket_update
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return socket_colors["NUMBER"]


class SN_IntSocket(bpy.types.NodeSocket):
    '''Int Socket for handeling integers'''
    bl_idname = 'SN_IntSocket'
    bl_label = "Integer"

    value: bpy.props.IntProperty(
        name="Int",
        description="Socket for an integer value",
        default=0,
        update=socket_update
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
            update=socket_update
        )

        def draw(self, context, layout, node, text):
            if self.is_output or self.is_linked:
                layout.label(text=text)
            else:
                row = layout.row()
                row.label(text=text)
                row.prop(self, "value", text=str(self.value), toggle=True)

        def draw_color(self, context, node):
            return socket_colors["BOOLEAN"]


class SN_DataSocket(bpy.types.NodeSocket):
    '''Socket that can be connected to everything'''
    bl_idname = 'SN_DataSocket'
    bl_label = "Data"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return socket_colors["DATA"]


class SN_VectorSocket(bpy.types.NodeSocket):
    '''Vector Socket for handeling vectors'''
    bl_idname = 'SN_VectorSocket'
    bl_label = "Vector"

    value: bpy.props.FloatVectorProperty(
        name="Vector",
        description="Socket for a vector value",
        update=socket_update
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            col = layout.column()
            col.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return socket_colors["VECTOR"]


class SN_EnumSocket(bpy.types.NodeSocket):
    '''Enum Socket for handling enums'''
    bl_idname = 'SN_EnumSocket'
    bl_label = "Enum"

    def get_items(self,context):
        return self.node.get_socket_items(self)

    value: bpy.props.EnumProperty(
        name="String",
        description="Socket for a string value",
        update=socket_update,
        items = get_items,
        default=None
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return socket_colors["STRING"]


class SN_LayoutSocket(bpy.types.NodeSocket):
    '''Layout Socket for connecting layouts'''
    bl_idname = 'SN_LayoutSocket'
    bl_label = "Layout"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

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


class SN_SceneDataSocket(bpy.types.NodeSocket):
    '''Scene Data Socket for data from the scene'''
    bl_idname = 'SN_SceneDataSocket'
    bl_label = "Scene Data"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return socket_colors["SCENE"]