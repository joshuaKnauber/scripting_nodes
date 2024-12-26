from email import header
from scripting_nodes.src.lib.editor.editor import in_sn_tree
import bpy


class SNA_PT_Settings(bpy.types.Panel):
    bl_idname = "SNA_PT_Settings"
    bl_label = "Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 1

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context):
        return


class SNA_PT_Dev_Settings(bpy.types.Panel):
    bl_idname = "SNA_PT_Dev_Settings"
    bl_label = "Development"
    bl_parent_id = "SNA_PT_Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 0

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context):
        layout = self.layout

        col = layout.column(heading="Logs")
        col.use_property_split = True
        col.use_property_decorate = False

        col.prop(context.scene.sna.dev, "log_tree_rebuilds")
        col.prop(context.scene.sna.dev, "log_reload_times")
