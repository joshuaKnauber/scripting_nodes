import bpy
from .nodes.node_looks import socket_colors

def update_socket_autocompile(self,context):
    context.space_data.node_tree.compiler.autocompile()

class SN_StringSocket(bpy.types.NodeSocket):
    '''String Socket for handling text'''
    bl_idname = 'SN_StringSocket'
    bl_label = "String"

    is_data_socket = True

    value: bpy.props.StringProperty(
        name="String",
        description="Socket for a string value",
        default="",
        update=update_socket_autocompile
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return socket_colors["STRING"]


class SN_EnumSocket(bpy.types.NodeSocket):
    '''Enum Socket for handling enums'''
    bl_idname = 'SN_EnumSocket'
    bl_label = "Enum"

    is_data_socket = True

    def get_items(self,context):
        return self.node.get_socket_items(self)

    value: bpy.props.EnumProperty(
        name="String",
        description="Socket for a string value",
        update=update_socket_autocompile,
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


class SN_NumberSocket(bpy.types.NodeSocket):
    '''Number Socket for handeling numbers'''
    bl_idname = 'SN_NumberSocket'
    bl_label = "Number"

    is_data_socket = True

    value: bpy.props.FloatProperty(
        name="Number",
        description="Socket for a number value",
        default=0,
        update=update_socket_autocompile
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return socket_colors["NUMBER"]


class SN_FactorSocket(bpy.types.NodeSocket):
    '''Number Socket for handeling factors'''
    bl_idname = 'SN_FactorSocket'
    bl_label = "Factor"

    is_data_socket = True

    value: bpy.props.FloatProperty(
        name="Factor",
        description="Socket for a number value",
        default=0,
        update=update_socket_autocompile,
        soft_min = 0,
        soft_max = 1
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text,slider=True)

    def draw_color(self, context, node):
        return socket_colors["NUMBER"]


class SN_BooleanSocket(bpy.types.NodeSocket):
    '''Boolean Socket for handeling booleans'''
    bl_idname = 'SN_BooleanSocket'
    bl_label = "Boolean"

    is_data_socket = True

    value: bpy.props.BoolProperty(
        name="Boolean",
        description="Socket for a boolean value",
        default=False,
        update=update_socket_autocompile
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


class SN_VectorSocket(bpy.types.NodeSocket):
    '''Vector Socket for handeling vectors'''
    bl_idname = 'SN_VectorSocket'
    bl_label = "Vector"

    is_data_socket = True

    value: bpy.props.FloatVectorProperty(
        name="Vector",
        description="Socket for a vector value",
        update=update_socket_autocompile
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

    is_data_socket = False

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return socket_colors["LAYOUT"]


class SN_SceneDataSocket(bpy.types.NodeSocket):
    '''Scene Data Socket for data from the scene'''
    bl_idname = 'SN_SceneDataSocket'
    bl_label = "Scene Data"

    is_data_socket = False

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return socket_colors["SCENE"]


class SN_ProgramSocket(bpy.types.NodeSocket):
    '''Program Socket for connecting nodes in the order they should be executed'''
    bl_idname = 'SN_ProgramSocket'
    bl_label = "Program"

    is_data_socket = False

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return socket_colors["PROGRAM"]

class SN_DataSocket(bpy.types.NodeSocket):
    '''Socket that can be connected to everything'''
    bl_idname = 'SN_DataSocket'
    bl_label = "Data"

    is_data_socket = True

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return socket_colors["DATA"]