import bpy
import platform


class SN_PT_HeaderSettings(bpy.types.Panel):
    bl_idname = "SN_PT_HeaderSettings"
    bl_label = "Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "HEADER"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.sn, "insert_sockets")
        layout.prop(
            context.preferences.view,
            "show_tooltips_python",
            text="Show Python Tooltips",
        )


def header_prepend(self, context):
    if (
        context.space_data.node_tree
        and context.space_data.node_tree.bl_idname == "ScriptingNodesTree"
    ):
        layout = self.layout
        row = layout.row()

        if len(context.space_data.node_tree.nodes) == 0:
            row.operator(
                "node.add_node", text="Tutorial", icon="PLAY", depress=True
            ).type = "SN_TutorialNode"

        row.operator("sn.show_data_overview", text="Blend Data", icon="RNA")

        subrow = row.row(align=True)
        if platform.system() == "Windows":
            subrow.operator("sn.clear_console", text="", icon="TRASH")
            subrow.operator("wm.console_toggle", text="Console", icon="CONSOLE")

        row.operator("screen.userpref_show", text="", icon="PREFERENCES")
        row.popover("SN_PT_HeaderSettings", text="", icon="WINDOW")

        if context.scene.sn.has_update:
            row.separator()
            row.operator("sn.update_message", text="Update!", icon="INFO", depress=True)


def header_append(self, context):
    if (
        context.space_data.node_tree
        and context.space_data.node_tree.bl_idname == "ScriptingNodesTree"
    ):
        layout = self.layout

        row = layout.row()
        sub_row = row.row(align=True)
        col = sub_row.column(align=True)
        col.scale_x = 1.5
        col.operator("sn.force_compile", text="", icon="FILE_REFRESH")
        sub_row.operator("sn.force_unregister", text="", icon="UNLINKED")
        sub_row = row.row(align=True)
        sub_row.operator(
            "wm.url_open",
            text="",
            icon_value=bpy.context.scene.sn_icons["discord"].icon_id,
        ).url = "https://discord.com/invite/NK6kyae"
        sub_row.operator(
            "wm.url_open", text="", icon="HELP"
        ).url = "https://joshuaknauber.notion.site/Serpens-Documentation-d44c98df6af64d7c9a7925020af11233"
        ms = round(context.scene.sn.compile_time * 1000, 2)
        row.label(text=str(ms) + "ms")
        row.prop(
            context.scene.sn,
            "pause_reregister",
            text="",
            icon="PLAY" if context.scene.sn.pause_reregister else "PAUSE",
        )


def node_info_append(self, context):
    layout = self.layout
    node = context.space_data.node_tree.nodes.active
    if getattr(node, "is_sn", False):
        layout.operator(
            "wm.url_open", text="Node Documentation", icon="QUESTION"
        ).url = "https://joshuaknauber.notion.site/555efb921f50426ea4d5812f1aa3e462?v=d781b590cc8f47449cb20812deab0cc6"


def footer_status(self, context):
    layout = self.layout
    sn = context.scene.sn
