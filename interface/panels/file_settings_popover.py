import bpy
import os


class SN_PT_FileSettingsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_FileSettingsPanel"
    bl_label = "Location"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "WINDOW"
    bl_ui_units_x = 10

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        layout.prop(sn, "use_external")
        layout.separator()

        col = layout.column(align=True)
        col.enabled = sn.use_external

        shortened_path = os.path.basename(sn.addon_location)
        row = col.row()
        row.scale_y = 1.2
        row.operator(
            "sn.select_location",
            text=shortened_path if shortened_path else "Select Addon",
            icon="FILE_FOLDER",
        )
        # col.separator(factor=2)
