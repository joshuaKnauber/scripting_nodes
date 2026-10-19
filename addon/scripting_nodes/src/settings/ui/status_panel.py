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
    """Above everything else: whether the add-on runs, the nodes with errors
    (in any tree) and the error that kept it from loading."""

    bl_idname = "SNA_PT_AddonStatus"
    bl_label = "Addon Error"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"HIDE_HEADER"}
    bl_order = -1

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        layout = self.layout
        broken = errors.nodes_with_errors()
        if broken:
            trees = sorted({node.id_data.name for node in broken})
            col = layout.column(align=True)
            row = col.row()
            row.alert = True
            count = len(broken)
            text = f"{count} error{'s' if count > 1 else ''} in {', '.join(trees)}"
            row.label(text=text, icon="ERROR")
            col.operator("sna.go_to_next_error", text="Go to Error", icon="VIEWZOOM")
        elif not errors.addon_error:
            row = layout.row()
            row.active = False
            running = context.scene.sna.addon.enabled
            row.label(
                text="Running, no errors" if running else "Not running (Addon)",
                icon="CHECKMARK" if running else "PAUSE",
            )
        if not errors.addon_error:
            return
        box = layout.box()
        box.alert = True
        row = box.row()
        row.label(text="The addon couldn't be loaded", icon="ERROR")
        row.operator("sna.copy_addon_error", text="", icon="COPYDOWN")
        col = box.column(align=True)
        col.scale_y = 0.8
        # system.ui_scale includes the display DPI (retina)
        char_px = 7 * context.preferences.system.ui_scale
        width = max(20, int((context.region.width - 40) / char_px))
        lines = []
        for line in errors.addon_error.strip().splitlines()[-MAX_LINES:]:
            lines.extend(textwrap.wrap(line, width) or [""])
        for line in lines[-MAX_LINES:]:
            col.label(text=line)
