import bpy


class SN_PT_VariablePanel(bpy.types.Panel):
    bl_idname = "SN_PT_VariablePanel"
    bl_label = "Variables"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return (
            context.space_data.tree_type == "ScriptingNodesTree"
            and context.space_data.node_tree
        )

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        ntree = context.space_data.node_tree
