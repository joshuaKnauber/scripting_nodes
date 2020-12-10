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
        tree = bpy.data.node_groups.new("NodeTree", "ScriptingNodesTree")
        tree.setup(is_graph=True, is_main=False, addon_tree=bpy.data.node_groups[context.scene.sn.editing_addon])
        return {"FINISHED"}
