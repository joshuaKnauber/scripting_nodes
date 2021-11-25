import bpy



class SN_PT_HeaderSettings(bpy.types.Panel):
    bl_idname = "SN_PT_HeaderSettings"
    bl_label = "Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "HEADER"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.sn, "minimal_header", text="Minimize Header", icon="FULLSCREEN_EXIT")
        layout.prop(context.scene.sn, "insert_sockets", icon="NODE_INSERT_OFF")
        layout.prop(context.scene.sn, "python_buttons", icon="COPYDOWN")
        layout.prop(context.preferences.view, "show_tooltips_python", text="Dev Tool Tips", icon="INFO")
        layout.operator("wm.console_toggle", text="Toggle System Console", icon="CONSOLE")



def prepend_header(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
        layout = self.layout

        addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences
        if context.scene.sn.has_update and addon_prefs.check_for_updates:
            row = layout.row()
            row.operator("sn.update_message", depress=True, text="Update Available!", icon="INFO")



def append_header(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree":

        layout = self.layout
