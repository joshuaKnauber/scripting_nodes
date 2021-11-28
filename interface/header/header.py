import bpy



class SN_PT_HeaderSettings(bpy.types.Panel):
    bl_idname = "SN_PT_HeaderSettings"
    bl_label = "Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "HEADER"

    def draw(self, context):
        layout = self.layout
        # layout.prop(context.scene.sn, "insert_sockets", icon="NODE_INSERT_OFF")
        # layout.prop(context.scene.sn, "python_buttons", icon="COPYDOWN")
        layout.prop(context.preferences.view, "show_tooltips_python", text="Dev Tool Tips", icon="INFO")
        layout.operator("wm.console_toggle", text="Toggle System Console", icon="CONSOLE")



def header_panel(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
        layout = self.layout

        row = layout.row()
        row.scale_x = 1.2
        row.operator("wm.url_open", text="",
                        icon_value=bpy.context.scene.sn_icons["discord"].icon_id).url = "https://discord.com/invite/NK6kyae"
        row.operator("wm.url_open", text="", icon_value=bpy.context.scene.sn_icons[
                        "bug"].icon_id).url = "https://joshuaknauber.github.io/visual_scripting_addon_docs/visual_scripting_docs/site/bugs/"

        row.popover("SN_PT_HeaderSettings", text="", icon="PREFERENCES")
