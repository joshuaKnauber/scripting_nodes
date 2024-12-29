from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
    sn_nodes,
)
import bpy


class SNA_OT_RegenerateAllNodes(bpy.types.Operator):
    bl_idname = "sna.regenerate"
    bl_label = "Regenerate All Nodes"
    bl_description = "Regenerates the code for all nodes in your addon"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context):
        for ntree in scripting_node_trees():
            for node in sn_nodes(ntree):
                node._generate()
        self.report({"INFO"}, "Regenerated all nodes")
        return {"FINISHED"}
