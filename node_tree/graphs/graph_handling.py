import bpy


class SN_OT_RemoveGraph(bpy.types.Operator):
    bl_idname = "sn.remove_graph"
    bl_label = "Remove Graph"
    bl_description = "Removes this graph from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    index: bpy.props.IntProperty(options={"SKIP_SAVE"})

    def execute(self, context):
        for node in bpy.data.node_groups[self.index].nodes:
            bpy.data.node_groups[self.index].nodes.remove(node)

        bpy.data.node_groups.remove(bpy.data.node_groups[self.index])
        bpy.context.scene.sn.node_tree_index = self.index-1 if self.index>0 else 0
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

