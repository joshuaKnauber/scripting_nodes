import bpy


class SN_OT_ExportAddon(bpy.types.Operator):
    """Export the current addon as a zip file"""
    bl_idname = "sn.export_addon"
    bl_label = "Export Addon"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context):
        return {"FINISHED"}
