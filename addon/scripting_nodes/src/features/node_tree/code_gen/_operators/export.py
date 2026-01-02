from ..generator import generate_addon
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
        context.scene.sna.addon.is_exporting = True

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
            generate_addon(dev_module=False, base_path=export_dir)

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
        finally:
            context.scene.sna.addon.is_exporting = False

        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = f"{bpy.context.scene.sna.addon.module_name}.zip"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
