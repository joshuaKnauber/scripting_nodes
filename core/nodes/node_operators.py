import bpy

from .Interface.PanelNode import SN_PanelNode


class SN_OT_NodeSettings(bpy.types.Operator):
    """Open the Node Settings panel"""
    bl_idname = "sn.node_settings"
    bl_label = "Node Settings"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty()

    def execute(self, context: bpy.types.Context):
        return {"FINISHED"}

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        node = bpy.context.space_data.edit_tree.nodes[self.node]

        row = layout.row()
        row.label(text=f"Settings '{node.name}'")
        layout.separator()

        if node.bl_idname == SN_PanelNode.bl_idname:
            panel_settings(layout, node)

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)


def panel_settings(layout: bpy.types.UILayout, node: bpy.types.Node):
    layout.prop(node, "label")
    layout.separator()
    row = layout.row()
    row.prop(node, "default_closed")
    row.prop(node, "hide_header")
    row = layout.row()
    row.prop(node, "expand_header")
    layout.separator()
    layout.prop(node, "order")
