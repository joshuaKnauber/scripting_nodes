import bpy


def prepend_header(self, context):
    layout = self.layout


def has_nodes(addon_tree):
    for graph in addon_tree.sn_graphs:
        if len(graph.node_tree.nodes):
            return True
    return False


def append_header(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree" and context.scene.sn.editing_addon != "NONE":

        layout = self.layout
        addon_tree = context.scene.sn.addon_tree()
        
        if len(context.space_data.node_tree.nodes) == 0 and context.space_data.node_tree == addon_tree:
            row = layout.row()
            row.operator("sn.start_tutorial",icon="QUESTION", depress=True)
        
        if has_nodes(addon_tree):
            row = layout.row(align=True)
            if context.scene.sn.active_addon_has_changes():
                row.operator("sn.compile",text="Compile",icon="FILE_REFRESH",depress=True)
            else:
                row.operator("sn.compile",text="Compiled",icon="CHECKMARK",depress=False)
            row.operator("sn.remove_addon",text="",icon="UNLINKED")
        
        layout.separator()

        layout.prop_tabs_enum(context.scene.sn, "bookmarks")

        row = layout.row(align=True)
        row.prop(context.scene.sn, "editing_addon", text="")
        row.operator("sn.create_addon",text="",icon="ADD")
        
        row = layout.row(align=True)
        row.operator("wm.url_open",text="",icon_value=bpy.context.scene.sn_icons[ "discord" ].icon_id).url = "https://discord.com/invite/NK6kyae"
        row.operator("wm.url_open",text="",icon_value=bpy.context.scene.sn_icons[ "bug" ].icon_id).url = "https://joshuaknauber.github.io/visual_scripting_addon_docs/visual_scripting_docs/site/bugs/"
