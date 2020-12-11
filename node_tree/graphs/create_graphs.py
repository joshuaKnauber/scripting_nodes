import bpy


class SN_OT_CreateGraph(bpy.types.Operator):
    bl_idname = "sn.add_graph"
    bl_label = "Add Graph"
    bl_description = "Adds a new graph to this addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        tree = bpy.data.node_groups.new("New Graph", "ScriptingNodesTree")
        addon_tree = context.scene.sn.addon_tree()
        tree.setup(addon_tree)
        return {"FINISHED"}



class SN_OT_RemoveGraph(bpy.types.Operator):
    bl_idname = "sn.remove_graph"
    bl_label = "Remove Graph"
    bl_description = "Removes this graph from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    index: bpy.props.IntProperty(options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        addon_tree = context.scene.sn.addon_tree()
        return addon_tree.sn_graph_index != 0

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        bpy.data.node_groups.remove(addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree)
        addon_tree.sn_graphs.remove(addon_tree.sn_graph_index)
        addon_tree.sn_graph_index -= 1
        return {"FINISHED"}