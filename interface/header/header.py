import bpy
from ...utils.is_serpens import in_sn_tree
from ...core.builder import builder


def header_prepend(self, context: bpy.types.Context):
    """Draws the UI for the start of the node editor header"""
    if in_sn_tree(context):
        layout = self.layout
        row = layout.row()

        row.operator("sna.toggle_browser", text="Blend Data Browser", icon="VIEWZOOM")


def header_append(self, context: bpy.types.Context):
    """Draws the UI for the end of the node editor header"""
    if in_sn_tree(context):
        sna = context.scene.sna
        layout = self.layout


def group_interface_append(self, context: bpy.types.Context):
    """Draws the UI for the node group interface"""
    if in_sn_tree(context):
        sna = context.scene.sna
        layout = self.layout
        layout.label(text="SERPENS Interface")
        layout.label(text="panels not supported")
