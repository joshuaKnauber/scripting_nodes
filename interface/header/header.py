import bpy



class SN_PT_HeaderSettings(bpy.types.Panel):
    bl_idname = "SN_PT_HeaderSettings"
    bl_label = "Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "HEADER"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.sn, "insert_sockets", icon="TRIA_UP")



def header_prepend(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
        layout = self.layout
        row = layout.row()

        if len(context.space_data.node_tree.nodes) == 0:
            row.operator("node.add_node", text="Start Tutorial", icon="PLAY", depress=True).type = "SN_TutorialNode"
            
        subrow = row.row(align=True)
        subrow.operator("sn.clear_console", text="", icon="TRASH")
        subrow.operator("wm.console_toggle", text="Console", icon="CONSOLE")
        row.prop(context.preferences.view, "show_tooltips_python", text="", icon="INFO")
        row.popover("SN_PT_HeaderSettings", text="", icon="PREFERENCES")

        if context.scene.sn.has_update:
            row.separator()
            row.operator("sn.update_message", text="Update!", icon="INFO", depress=True)




def header_append(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
        layout = self.layout

        row = layout.row()
        sub_row = row.row(align=True)
        col = sub_row.column(align=True)
        col.scale_x = 1.5
        col.operator("sn.force_compile", text="", icon="FILE_REFRESH")
        sub_row.operator("sn.force_unregister", text="", icon="UNLINKED")
        row.operator("wm.url_open", text="", icon_value=bpy.context.scene.sn_icons["discord"].icon_id).url = "https://discord.com/invite/NK6kyae"
        row.operator("wm.url_open", text="", icon_value=bpy.context.scene.sn_icons["bug"].icon_id).url = "https://joshuaknauber.github.io/visual_scripting_addon_docs/visual_scripting_docs/site/bugs/"