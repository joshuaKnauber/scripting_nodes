import bpy


class SN_OT_Compile(bpy.types.Operator):
    bl_idname = "sn.compile"
    bl_label = "Compile"
    bl_description = "Compiles all graphs with changes"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        for graph in addon_tree.sn_graphs:
            if graph.node_tree.has_changes:
                graph.node_tree.has_changes = False
        return {"FINISHED"}
