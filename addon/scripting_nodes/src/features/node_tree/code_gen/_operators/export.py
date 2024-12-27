from scripting_nodes.src.features.node_tree.code_gen.generator import generate_addon
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
        path = (
            self.filepath + ".zip"
            if not self.filepath.endswith(".zip")
            else self.filepath
        )

        # generate addon folder
        folder_path = os.path.join(
            os.path.dirname(path), bpy.context.scene.sna.addon.module_name
        )
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        generate_addon(dev_module=False, base_path=os.path.dirname(path))

        # zip folder
        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(folder_path):
            parent_dir = os.path.dirname(folder_path)
            folder_name = os.path.basename(folder_path)
            shutil.make_archive(path[:-4], "zip", parent_dir, folder_name)
            shutil.rmtree(folder_path)

        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = f"{bpy.context.scene.sna.addon.module_name}.zip"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
