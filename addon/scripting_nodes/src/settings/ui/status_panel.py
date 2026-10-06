import textwrap

import bpy

from ...core import errors
from ...node_tree.editor import in_sn_tree

MAX_LINES = 12


class SNA_OT_CopyAddonError(bpy.types.Operator):
    bl_idname = "sna.copy_addon_error"
    bl_label = "Copy Error"
    bl_description = "Copy the full error message to the clipboard"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        context.window_manager.clipboard = errors.addon_error or ""
        return {"FINISHED"}


class SNA_PT_AddonStatus(bpy.types.Panel):
    """Shown above everything else while the generated addon has an error."""

    bl_idname = "SNA_PT_AddonStatus"
    bl_label = "Addon Error"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"HIDE_HEADER"}
    bl_order = -1

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context) and bool(errors.addon_error)

    def draw(self, context):
        box = self.layout.box()
        box.alert = True
        row = box.row()
        row.label(text="The addon couldn't be loaded", icon="ERROR")
        row.operator("sna.copy_addon_error", text="", icon="COPYDOWN")
        col = box.column(align=True)
        col.scale_y = 0.8
        width = max(
            20, int(context.region.width / (7 * context.preferences.view.ui_scale))
        )
        lines = []
        for line in errors.addon_error.strip().splitlines()[-MAX_LINES:]:
            lines.extend(textwrap.wrap(line, width) or [""])
        for line in lines[-MAX_LINES:]:
            col.label(text=line)
