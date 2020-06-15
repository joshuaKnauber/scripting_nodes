import bpy


class SN_OT_FindErrorNode(bpy.types.Operator):
    bl_idname = "scripting_nodes.find_error_node"
    bl_label = "Find error node"
    bl_description = "Finds the node which is causing the error"
    bl_options = {"REGISTER","INTERNAL"}

    node_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        found = False
        if context.space_data.tree_type == "ScriptingNodesTree":
            for node in context.space_data.node_tree.nodes:
                if node.name == self.node_name:
                    found = True
                    node.select = True
                    bpy.ops.node.view_selected()
                else:
                    node.select = False
        if not found:
            self.report({"INFO"},message ="Couldn't find the corresponding node. Try to reload the node tree.")
        return {"FINISHED"}