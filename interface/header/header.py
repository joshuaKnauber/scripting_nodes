import bpy


def prepend_header(self, context):
    layout = self.layout


def append_header(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree" and context.scene.sn.editing_addon != "NONE":

        layout = self.layout
        
        row = layout.row(align=True)
        if context.scene.sn.active_addon_has_changes():
            row.operator("sn.compile",text="Compile",icon="FILE_REFRESH",depress=True)
        else:
            row.operator("sn.compile",text="Compiled",icon="CHECKMARK",depress=False)
        row.operator("sn.remove_addon",text="",icon="UNLINKED")
        
        layout.separator()

        layout.prop_tabs_enum(context.scene.sn, "bookmarks")

        layout.prop(context.scene.sn, "editing_addon", text="")