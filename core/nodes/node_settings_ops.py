import bpy

from ..utils.nodes import get_node_by_id
from .Interface.SubPanelNode import SNA_NodeSubpanel
from .Interface.PanelNode import SNA_NodePanel


class SNA_OT_NodeSettings(bpy.types.Operator):
    """Open the Node Settings panel"""

    bl_idname = "sna.node_settings"
    bl_label = "Node Settings"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty()

    def execute(self, context: bpy.types.Context):
        return {"FINISHED"}

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        node = get_node_by_id(self.node)

        row = layout.row()
        row.label(text=f"Settings '{node.name}'")
        layout.separator()

        if node.bl_idname == SNA_NodePanel.bl_idname:
            panel_settings(layout, node)
        elif node.bl_idname == SNA_NodeSubpanel.bl_idname:
            subpanel_settings(layout, node)

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)


def panel_settings(layout: bpy.types.UILayout, node: bpy.types.Node):
    layout.prop(node, "title")
    layout.separator()
    row = layout.row()
    row.prop(node, "default_closed")
    row.prop(node, "hide_header")
    row = layout.row()
    row.prop(node, "expand_header")
    row.prop(node, "order")
    layout.separator()
    layout.label(text="Picked Settings")
    row = layout.row()
    row.prop(node, "space")
    row.prop(node, "region")
    row = layout.row()
    row.prop(node, "category")
    row.prop(node, "context")


def subpanel_settings(layout: bpy.types.UILayout, node: bpy.types.Node):
    layout.prop(node, "title")
    layout.separator()
    row = layout.row()
    row.prop(node, "default_closed")
    row.prop(node, "hide_header")
    row = layout.row()
    row.prop(node, "expand_header")
    row.prop(node, "order")
    layout.separator()
    layout.prop(node, "origin")
    if node.origin == "BLENDER":
        layout.separator()
        layout.label(text="Picked Settings")
        layout.prop(node, "blender_panel")
        row = layout.row()
        row.prop(node, "blender_space")
        row.prop(node, "blender_region")
        row = layout.row()
        row.prop(node, "blender_category")
        row.prop(node, "blender_context")
