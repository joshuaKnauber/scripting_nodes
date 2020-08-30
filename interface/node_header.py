import bpy

class SN_PT_TutorialSettingsPopover(bpy.types.Panel):
    bl_idname = "SN_PT_TutorialSettingsPopover"
    bl_label = "Display Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "HEADER"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.sn_properties,"tutorial_scale",text="Display Scale", slider=True)


def node_header(self, context):
    if context.space_data.node_tree:
        if context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
            if context.space_data.node_tree.nodes.active:
                row = self.layout.row(align=True)
                col = row.column(align=True)
                col.enabled = not context.scene.sn_properties.show_marketplace
                col.prop(context.scene.sn_properties,"show_node_info",text="", icon="QUESTION", toggle=True)
                col = row.column(align=True)
                col.enabled = not context.scene.sn_properties.show_node_info
                col.prop(context.scene.sn_properties,"show_marketplace",text="", icon="IMAGE", toggle=True)
                row.popover("SN_PT_TutorialSettingsPopover",text="")

            row = self.layout.row(align=True)
            row.operator("scripting_nodes.compile_active", icon="FILE_REFRESH")
            row.operator("scripting_nodes.unregister_active", text="", icon="UNLINKED")
            row.separator()
    if context.space_data.tree_type == "ScriptingNodesTree":
        self.layout.prop(context.scene.sn_properties,"examples",text="")