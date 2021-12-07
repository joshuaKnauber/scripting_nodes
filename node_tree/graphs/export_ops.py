from bpy_extras.io_utils import ExportHelper
import bpy
import os
import shutil
from .node_tree import compile_all, unregister_all



class SN_OT_ExportAddon(bpy.types.Operator, ExportHelper):
    bl_idname = "sn.export_addon"
    bl_label = "Export Addon"
    bl_description = "Exports this addon to an installable zip file"
    bl_options = {"REGISTER", "INTERNAL"}

    filepath: bpy.props.StringProperty(
        name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    filename_ext = ".zip"
    filter_glob: bpy.props.StringProperty(default='*.zip', options={'HIDDEN'})

    def create_files(self, path):
        """ Creates the addon files in the folder structure """
        pass

    def create_structure(self, path):
        """ Sets up the addons folder structure at the given filepath """
        os.mkdir(path)
        baseDir = os.path.join(path, os.path.basename(path))
        os.mkdir(baseDir)
        os.mkdir(os.path.join(baseDir, "assets"))
        os.mkdir(os.path.join(baseDir, "icons"))
        return baseDir

    def zip_addon(self, path):
        """ Zips the given path """
        shutil.make_archive(path, 'zip', root_dir=path)
        try:
            shutil.rmtree(path)
        except OSError as e:
            self.report({"WARNING"}, message=f"Error: {e.filename} - {e.strerror}.")
    
    def execute(self, context):
        name, _ = os.path.splitext(self.filepath)
        if os.path.exists(name):
            self.report({"ERROR"}, message=f"Please delete the '{os.path.basename(name)}' folder before exporting.")
        else:
            baseDir = self.create_structure(name)
            self.create_files(baseDir)
            self.zip_addon(name)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = "fgjpesgp.zip"
        wm = context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}