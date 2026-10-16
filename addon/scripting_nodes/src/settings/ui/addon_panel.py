import textwrap

from ...core import compiler, export_check, metadata
from ...node_tree.editor import in_sn_tree
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


def _labeled(layout, text):
    """A row with `text` in the label column (like use_property_split)."""
    split = layout.split(factor=0.4)
    label = split.row()
    label.alignment = "RIGHT"
    label.label(text=text)
    row = split.row(align=True)
    row.use_property_split = False
    return row


def _version_row(layout, owner, prop, text):
    """Major, minor, patch side by side (split layouts stack arrays)."""
    row = _labeled(layout, text)
    for i in range(3):
        row.prop(owner, prop, index=i, text="")


class SNA_PT_Metadata_Settings(bpy.types.Panel):
    """What Blender shows about the add-on (blender_manifest.toml, bl_info)."""

    bl_idname = "SNA_PT_Metadata_Settings"
    bl_label = "Metadata"
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
        col.prop(addon, "tagline", placeholder=metadata.DEFAULT_TAGLINE)
        col.prop(addon, "author", placeholder="Unknown")
        col.prop(addon, "email")
        _version_row(col, addon, "version", "Version")
        col.prop(addon, "website", placeholder="https://")
        col.prop(addon, "location", placeholder="View3D > Sidebar")
        _labeled(col, "Tags").prop_menu_enum(
            addon, "tags", text=", ".join(sorted(addon.tags)) or "None"
        )
        col.separator()
        col.prop(addon, "copyright", placeholder="Your Name")
        col.separator()
        _version_row(col, addon, "blender_version_min", "Blender")
        row = _labeled(col, "Up To")
        row.prop(addon, "use_blender_version_max", text="")
        sub = row.row(align=True)
        sub.active = addon.use_blender_version_max
        for i in range(3):
            sub.prop(addon, "blender_version_max", index=i, text="")

        col = layout.column(heading="Permissions")
        col.use_property_split = True
        col.use_property_decorate = False
        for name, label, reason in metadata.PERMISSIONS:
            if name in compiler.used_permissions:
                # needed by nodes (File nodes, ...): always asked for
                row = _labeled(col, label)
                row.label(text="Used by nodes", icon="CHECKBOX_HLT")
                col.prop(addon, f"{name}_reason", placeholder=reason)
                continue
            col.prop(addon, f"permission_{name}")
            if getattr(addon, f"permission_{name}"):
                col.prop(addon, f"{name}_reason", placeholder=reason)

        for problem in metadata.problems(addon):
            layout.label(text=problem, icon="ERROR")


class SNA_PT_Overwrite_Settings(bpy.types.Panel):
    bl_idname = "SNA_PT_Overwrite_Settings"
    bl_label = "Overwrites"
    bl_parent_id = "SNA_PT_Addon_Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 1

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
        field_with_hint("class_prefix_overwrite", f"{addon.class_prefix}_PT_MyPanel")
        field_with_hint(
            "idname_namespace_overwrite", f"{addon.idname_namespace}.my_operator"
        )


class SNA_PT_Export_Check(bpy.types.Panel):
    """What reviewers of extensions.blender.org would ask to change."""

    bl_idname = "SNA_PT_Export_Check"
    bl_label = "Extensions Platform"
    bl_parent_id = "SNA_PT_Addon_Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("sna.check_export", icon="CHECKMARK")
        row.operator("wm.url_open", text="", icon="HELP").url = export_check.GUIDELINES
        if not export_check.checked:
            layout.label(text="Checked when you export", icon="INFO")
            return
        if not export_check.last:
            layout.label(text="Nothing to fix", icon="CHECKMARK")
            return
        # labels don't wrap: characters that fit next to the button
        scale = context.preferences.system.ui_scale
        width = max(16, int((context.region.width / scale - 80) / 7))
        col = layout.column(align=True)
        for issue in export_check.last:
            row = col.box().row()
            text = row.column(align=True)
            text.alert = issue.severity == "ERROR"
            icon = "ERROR" if issue.severity == "ERROR" else "INFO"
            for i, part in enumerate(_wrap(issue.message, width)):
                text.label(text=part, icon=icon if i == 0 else "BLANK1")
            if issue.node_id:
                op = row.operator("sna.go_to_node", text="", icon="VIEWZOOM")
                op.node_id = issue.node_id


def _wrap(text, width):
    """Lines of at most `width` characters (labels don't wrap)."""
    return textwrap.wrap(text, width) or [""]
