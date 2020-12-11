import bpy


def prepend_header(self, context):
    layout = self.layout


def append_header(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree" and context.scene.sn.editing_addon != "NONE":

        layout = self.layout

        layout.prop_tabs_enum(context.scene.sn, "bookmarks")

        layout.prop(context.scene.sn, "editing_addon", text="")