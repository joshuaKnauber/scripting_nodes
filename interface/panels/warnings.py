import bpy


def append_warning(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
        layout = self.layout
        row = layout.row()
        row.alert = True
        
        row.label(text="Do not edit these settings!", icon="ERROR")


def append_name_warning(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
        node = context.space_data.node_tree.nodes.active
        layout = self.layout
        
        layout.prop(node, "edit_name", text="Title", icon="FILE_SCRIPT")
        
        col = layout.column()
        col.alert = True
        col.label(text="Use 'Title' instead of the 'Name'!", icon="ERROR")
        col.label(text="Editing Name will cause issues!")
        layout.label(text="You can still edit Label normally", icon="INFO")