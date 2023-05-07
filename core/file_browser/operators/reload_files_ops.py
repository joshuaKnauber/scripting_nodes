import bpy
from ..load_files import load_files


class SN_OT_ReloadFiles(bpy.types.Operator):
    bl_idname = "sn.reload_files"
    bl_label = "Reload Files"
    bl_description = "Reloads the files in the file list"

    def execute(self, context):
        load_files(context.scene.sn.addon_location)
        self.report({"INFO"}, "Reload Complete")
        return {"FINISHED"}
