from bpy_extras.io_utils import ExportHelper
import bpy
import os
import shutil
from ...nodes.compiler import (
    format_blender_manifest,
    format_multifile,
    format_single_file,
)
from ...utils import normalize_code


class SN_OT_ExportAddon(bpy.types.Operator, ExportHelper):
    bl_idname = "sn.export_addon"
    bl_label = "Export Addon"
    bl_description = "Exports this addon to an installable zip file"
    bl_options = {"REGISTER", "INTERNAL"}

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype="FILE_PATH",
    )

    filename_ext = ".zip"
    filter_glob: bpy.props.StringProperty(default="*.zip", options={"HIDDEN"})

    def add_easy_bpy(self, path, code):
        """Adds the easybpy file to the addon if needed"""
        if "easybpy" in code and bpy.context.scene.sn.easy_bpy_path:
            shutil.copyfile(
                src=bpy.context.scene.sn.easy_bpy_path,
                dst=os.path.join(path, "easybpy.py"),
            )

    def add_assets(self, asset_path):
        """Adds the addon assets to the folder"""
        for asset in bpy.context.scene.sn.assets:
            if os.path.exists(asset.path):
                if os.path.isdir(asset.path):
                    dirname = os.path.basename(asset.path)
                    if not dirname:
                        dirname = os.path.basename(os.path.dirname(asset.path))
                    shutil.copytree(
                        asset.path,
                        os.path.join(asset_path, dirname),
                        dirs_exist_ok=True,
                    )
                else:
                    shutil.copy(
                        asset.path,
                        os.path.join(asset_path, os.path.basename(asset.path)),
                    )

    def add_icons(self, icon_path):
        """Adds the icons to the folder"""
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if node.bl_idname == "SN_IconNode":
                        if node.icon_source == "CUSTOM" and node.icon_file:
                            img_path = bpy.path.abspath(node.icon_file.filepath)
                            if os.path.exists(img_path):
                                filepath = os.path.join(
                                    icon_path, os.path.basename(img_path)
                                )
                                shutil.copy(img_path, filepath)
                            else:
                                raise FileNotFoundError(
                                    f"Could not find the icon file at {icon_path}"
                                )

    def add_code(self, path):
        """Creates the index file"""
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                ntree.reevaluate()
        if bpy.context.scene.sn.multifile:
            files = format_multifile()
        else:
            files = {
                "__init__.py": format_single_file(),
                "blender_manifest.toml": format_blender_manifest(),
            }
        for name in files.keys():
            with open(os.path.join(path, name), "a") as code_file:
                code = files[name]
                code = code.replace("from easybpy import", "from .easybpy import")
                code_file.write(code)
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                ntree.reevaluate()
        return code

    def create_files(self, path):
        """Creates the addon files in the folder structure"""
        self.add_assets(os.path.join(path, "assets"))
        self.add_icons(os.path.join(path, "icons"))
        code = self.add_code(path)
        self.add_easy_bpy(path, code)

    def create_structure(self, path):
        """Sets up the addons folder structure at the given filepath"""
        os.mkdir(path)
        baseDir = os.path.join(path, bpy.context.scene.sn.module_name)
        os.mkdir(baseDir)
        os.mkdir(os.path.join(baseDir, "assets"))
        os.mkdir(os.path.join(baseDir, "icons"))
        return baseDir

    def zip_addon(self, path):
        """Zips the given path"""
        shutil.make_archive(path, "zip", root_dir=path)
        try:
            shutil.rmtree(path)
        except OSError as e:
            self.report({"WARNING"}, message=f"Error: {e.filename} - {e.strerror}.")

    def execute(self, context):
        bpy.context.scene.sn.is_exporting = True
        context.window_manager.progress_begin(0, 100)
        try:
            name, _ = os.path.splitext(self.filepath)
            if os.path.exists(name):
                self.report(
                    {"ERROR"},
                    message=f"Please delete the '{os.path.basename(name)}' folder before exporting.",
                )
            else:
                baseDir = self.create_structure(name)
                context.window_manager.progress_update(30)
                self.create_files(baseDir)
                context.window_manager.progress_update(90)
                self.zip_addon(name)
            bpy.ops.sn.export_to_marketplace("INVOKE_DEFAULT")
        except Exception as e:
            self.report({"ERROR"}, message=f"Error: {e}")
        bpy.context.scene.sn.is_exporting = False
        context.window_manager.progress_end()
        return {"FINISHED"}

    def invoke(self, context, event):
        version = ".".join([str(i) for i in context.scene.sn.version])
        self.filepath = f"{context.scene.sn.module_name}_{version}.blend"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
