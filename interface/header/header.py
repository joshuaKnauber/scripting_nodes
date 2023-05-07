import bpy


def header_prepend(self, context):
    if (
        context.space_data.node_tree
        and context.space_data.node_tree.bl_idname == "ScriptingNodesTree"
    ):
        layout = self.layout
        row = layout.row()


def header_append(self, context):
    if (
        context.space_data.node_tree
        and context.space_data.node_tree.bl_idname == "ScriptingNodesTree"
    ):
        sn = context.scene.sn
        layout = self.layout
        layout.label(text=str(round(sn.last_generate_time*1000, 2)) + "ms")
