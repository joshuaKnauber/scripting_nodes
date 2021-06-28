import bpy


class SN_PT_HeaderSettings(bpy.types.Panel):
    bl_idname = "SN_PT_HeaderSettings"
    bl_label = "Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "HEADER"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.sn, "minimal_header",
                    text="Minimize Header", icon="FULLSCREEN_EXIT")
        layout.prop(context.scene.sn, "insert_sockets", icon="NODE_INSERT_OFF")
        layout.prop(context.scene.sn, "python_buttons", icon="COPYDOWN")
        layout.prop(context.preferences.view, "show_tooltips_python",
                    text="Dev Tool Tips", icon="INFO")
        layout.operator("wm.console_toggle",
                        text="Toggle System Console", icon="CONSOLE")


def example_dropdown(self, context):
    if context.space_data.tree_type == "ScriptingNodesTree":
        if not context.scene.sn.minimal_header:
            layout = self.layout
            layout.prop(context.scene.sn, "example_dropdown", text="")


def prepend_header(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.bl_idname == "ScriptingNodesTree":
        layout = self.layout
        addon_prefs = context.preferences.addons[__name__.partition('.')[
            0]].preferences
        if context.scene.sn.has_update and addon_prefs.check_for_updates:
            row = layout.row()
            row.alert = True
            row.operator("sn.update_message",
                         text="Update Available!", icon="INFO")


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
            row.operator("sn.start_tutorial", icon="QUESTION", depress=True)

        if has_nodes(addon_tree):
            row = layout.row(align=True)
            if context.scene.sn.active_addon_has_changes():
                row.operator("sn.compile", text="Compile",
                             icon="FILE_REFRESH", depress=True)
            else:
                row.operator("sn.compile", text="Compiled",
                             icon="CHECKMARK", depress=False)
            row.operator("sn.remove_addon", text="", icon="UNLINKED")

        layout.separator()

        layout.prop_tabs_enum(context.scene.sn, "bookmarks")

        if not context.scene.sn.minimal_header:
            row = layout.row(align=True)
            row.prop(context.scene.sn, "editing_addon", text="")
            row.operator("sn.create_addon", text="", icon="ADD")
            row.operator("sn.delete_addon", text="", icon="TRASH")

            row = layout.row(align=True)
            row.operator("wm.url_open", text="",
                         icon_value=bpy.context.scene.sn_icons["discord"].icon_id).url = "https://discord.com/invite/NK6kyae"
            row.operator("wm.url_open", text="", icon_value=bpy.context.scene.sn_icons[
                         "bug"].icon_id).url = "https://joshuaknauber.github.io/visual_scripting_addon_docs/visual_scripting_docs/site/bugs/"

        layout.popover("SN_PT_HeaderSettings", text="", icon="PREFERENCES")
