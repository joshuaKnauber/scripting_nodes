import bpy
from ..operators.tutorial_ops import get_tut_images


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

        if context.scene.sn_properties.show_tutorial:
            col = row.column(align=True)
            col.scale_x = 1.5
            col.enabled = context.scene.sn_properties.tut_index != 0
            col.operator("scripting_nodes.next_tutorial",text="",icon="FRAME_PREV").previous = True

            msg = str(context.scene.sn_properties.tut_index+1) + "/" + str(len(get_tut_images()))
            row.prop(context.scene.sn_properties,"show_tutorial",text=msg, toggle=True)

            col = row.column(align=True)
            col.scale_x = 1.5
            col.operator("scripting_nodes.next_tutorial",text="",icon="FRAME_NEXT").previous = False

        elif context.scene.sn_properties.show_node_info:
            row.prop(context.scene.sn_properties,"show_node_info",text="", icon="QUESTION", toggle=True)

        else:
            if not context.preferences.addons[__name__.partition('.')[0]].preferences.has_seen_tutorial:
                col = row.column(align=True)
                col.alert = True
                col.prop(context.preferences.addons[__name__.partition('.')[0]].preferences,"has_seen_tutorial",text="Show Tutorial", icon="HELP", toggle=True)
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

        row = self.layout.row(align=True)
        row.operator("wm.url_open",text="Report a Bug",icon_value=bpy.context.scene.sn_icons[ "bug" ].icon_id).url = "https://joshuaknauber.github.io/visual_scripting_addon_docs/visual_scripting_docs/site/bugs/"
        row.operator("wm.url_open",text="",icon_value=bpy.context.scene.sn_icons[ "discord" ].icon_id).url = "https://discord.com/invite/NK6kyae"
