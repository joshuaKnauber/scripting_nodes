import bpy


def append_warning(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
        layout = self.layout
        row = layout.row()
        row.alert = True
        
        row.label(text="Do not edit these settings!", icon="ERROR")