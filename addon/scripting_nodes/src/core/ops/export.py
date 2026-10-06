from ..generator import generate_addon
from ..build_context import set_building
import os
import bpy
import shutil


class SNA_OT_ExportAddon(bpy.types.Operator):
    bl_idname = "sna.export_addon"
    bl_label = "Export Addon"
    bl_description = "Export the current file as an addon"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(subtype="DIR_PATH")
    filter_folder: bpy.props.BoolProperty(default=True, options={"HIDDEN"})

    def execute(self, context):
        try:
            # Ensure filepath ends with .zip
            path = self.filepath
            if not path.endswith(".zip"):
                path = path + ".zip"

            # generate addon folder
            export_dir = os.path.dirname(path)
            module_name = bpy.context.scene.sna.addon.module_name
            folder_path = os.path.join(export_dir, module_name)

            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

            # Flag emitted as build-time so nodes strip dev-only affordances
            # (e.g. Print's SN overlay hook). Wrapped in try/finally so a
            # codegen error can never leave the live editor in build mode.
            set_building(True)
            try:
                generate_addon(base_path=export_dir)
            finally:
                set_building(False)

            # zip folder
            if os.path.exists(path):
                os.remove(path)
            if os.path.exists(folder_path):
                # Create zip with folder contents at root level (for extension compatibility)
                shutil.make_archive(path[:-4], "zip", folder_path)
                shutil.rmtree(folder_path)
                self.report({"INFO"}, f"Exported to {path}")
            else:
                self.report(
                    {"ERROR"}, f"Failed to generate addon folder: {folder_path}"
                )
        except Exception as e:
            self.report({"ERROR"}, f"Export failed: {str(e)}")
            import traceback

            traceback.print_exc()

        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = f"{bpy.context.scene.sna.addon.module_name}.zip"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
