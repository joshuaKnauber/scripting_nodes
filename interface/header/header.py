import bpy
from ...utils.is_serpens import in_sn_tree
from ...core.builder import builder


def header_prepend(self, context: bpy.types.Context):
    """Draws the UI for the start of the node editor header"""
    if in_sn_tree(context):
        layout = self.layout
        row = layout.row()


def header_append(self, context: bpy.types.Context):
    """Draws the UI for the end of the node editor header"""
    if in_sn_tree(context):
        sna = context.scene.sna
        layout = self.layout
