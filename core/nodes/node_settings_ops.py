import bpy

from ..utils.nodes import get_node_by_id
from .Interface import SubPanelNode
from .Interface import PanelNode


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

        if node.bl_idname == PanelNode.SNA_NodePanel.bl_idname:
            PanelNode.draw_settings(layout, node)
        elif node.bl_idname == SubPanelNode.SNA_NodeSubpanel.bl_idname:
            SubPanelNode.draw_settings(layout, node)

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)
