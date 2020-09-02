import bpy

class SN_PT_TutorialSettingsPopover(bpy.types.Panel):
    bl_idname = "SN_PT_TutorialSettingsPopover"
    bl_label = "Display Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "HEADER"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.sn_properties,"tutorial_scale",text="Display Scale", slider=True)
        layout.prop(context.scene.sn_properties,"show_python_docs")


def node_header(self, context):
    if context.space_data.tree_type == "ScriptingNodesTree":
        row = self.layout.row(align=True)

        if not context.preferences.addons[__name__.partition('.')[0]].preferences.has_seen_tutorial:
            col = row.column(align=True)
            col.alert = True
            col.prop(context.scene.sn_properties,"show_tutorial",text="Show Tutorial", icon="HELP", toggle=True)
        else:
            row.prop(context.scene.sn_properties,"show_tutorial",text="", icon="HELP", toggle=True)

        if context.space_data.node_tree and context.space_data.node_tree.nodes.active:
            row.prop(context.scene.sn_properties,"show_node_info",text="", icon="QUESTION", toggle=True)

        row.popover("SN_PT_TutorialSettingsPopover",text="")

        if context.space_data.node_tree:
            row = self.layout.row(align=True)
            row.operator("scripting_nodes.compile_active", icon="FILE_REFRESH")
            row.operator("scripting_nodes.unregister_active", text="", icon="UNLINKED")
            row.separator()
            
        self.layout.prop(context.scene.sn_properties,"examples",text="")