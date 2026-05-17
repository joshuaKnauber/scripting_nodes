from .....lib.editor.editor import in_sn_tree
import bpy


class SNA_PT_Addon_Settings(bpy.types.Panel):
    bl_idname = "SNA_PT_Addon_Settings"
    bl_label = ""
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED", "HEADER_LAYOUT_EXPAND"}
    bl_order = 0

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw_header(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.separator()
        row.prop(context.scene.sna.addon, "enabled", text="")
        row.label(text="Addon")

    def draw(self, context):
        layout = self.layout
        layout.enabled = context.scene.sna.addon.enabled

        col = layout.column(heading="Info")
        col.use_property_split = True
        col.use_property_decorate = False

        col.prop(context.scene.sna.addon, "addon_name")

        layout.separator()

        col = layout.column(heading="Build")
        col.use_property_split = True
        col.use_property_decorate = False

        col.prop(context.scene.sna.addon, "persist_addon")

        layout.separator()

        row = layout.row()
        row.scale_y = 1.5
        row.operator("sna.export_addon", icon="EXPORT")


class SNA_PT_Overwrite_Settings(bpy.types.Panel):
    bl_idname = "SNA_PT_Overwrite_Settings"
    bl_label = "Overwrites"
    bl_parent_id = "SNA_PT_Addon_Settings"
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
        addon = context.scene.sna.addon

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False

        def field_with_hint(prop_name, example):
            col.prop(addon, prop_name)
            hint = col.row()
            hint.alignment = "RIGHT"
            hint.active = False
            hint.label(text=example)
            col.separator(factor=0.5)

        field_with_hint("module_name_overwrite", f"import {addon.module_name}")
        field_with_hint(
            "class_prefix_overwrite", f"{addon.class_prefix}_PT_MyPanel"
        )
        field_with_hint(
            "idname_namespace_overwrite", f"{addon.idname_namespace}.my_operator"
        )
