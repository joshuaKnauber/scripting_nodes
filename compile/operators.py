import bpy

class SN_OT_EmptyOperator(bpy.types.Operator):
    bl_idname = "scripting_nodes.empty"
    bl_label = "Empty Operator"
    bl_description = "This is an empty operator"
    bl_options = {"REGISTER","INTERNAL"}

    def execute(self, context):        
        return {"FINISHED"}


class SN_OT_ReloadButton(bpy.types.Operator):
    bl_idname = "scripting_nodes.compile"
    bl_label = "Reload"
    bl_description = "Compiles the Nodetree"
    bl_options = {"REGISTER","INTERNAL"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        context.space_data.node_tree.compiler.recompile()
        return {"FINISHED"}


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


class SN_OT_RemoveButton(bpy.types.Operator):
    bl_idname = "scripting_nodes.remove_nodetree"
    bl_label = "Delete"
    bl_description = "Delete the active Nodetree"
    bl_options = {"REGISTER","INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        treeName = context.space_data.node_tree.name
        #TODO unregister tree
        bpy.data.node_groups.remove(bpy.data.node_groups[treeName])
        if len(bpy.data.node_groups) > 0:
            context.space_data.node_tree = bpy.data.node_groups[0]
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
