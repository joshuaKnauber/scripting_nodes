import bpy


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
        layout.label(text="Node Settings")
        layout.label(text=node.name)

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)
