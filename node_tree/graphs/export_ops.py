from bpy_extras.io_utils import ExportHelper
import bpy
import os
import shutil
from ...nodes.compiler import format_single_file
from ...utils import normalize_code



class SN_OT_ExportAddon(bpy.types.Operator, ExportHelper):
    bl_idname = "sn.export_addon"
    bl_label = "Export Addon"
    bl_description = "Exports this addon to an installable zip file"
    bl_options = {"REGISTER", "INTERNAL"}

    filepath: bpy.props.StringProperty(
        name="File Path", description="Filepath used for exporting the file", maxlen=1024, subtype='FILE_PATH')

    filename_ext = ".zip"
    filter_glob: bpy.props.StringProperty(default='*.zip', options={'HIDDEN'})
    
    def add_easy_bpy(self, path, code):
        """ Adds the easybpy file to the addon if needed """
        if "easybpy" in code and bpy.context.scene.sn.easy_bpy_path:
            shutil.copyfile(src=bpy.context.scene.sn.easy_bpy_path, dst=os.path.join(path, "easybpy.py"))

    def add_assets(self, asset_path):
        """ Adds the addon assets to the folder """
        for asset in bpy.context.scene.sn.assets:
            if os.path.exists(asset.path):
                if os.path.isdir(asset.path):
                    dirname = os.path.basename(asset.path)
                    if not dirname: dirname = os.path.basename(os.path.dirname(asset.path))
                    shutil.copytree(asset.path, os.path.join(asset_path, dirname), dirs_exist_ok=True)
                else:
                    shutil.copy(asset.path, os.path.join(asset_path, os.path.basename(asset.path)))

    def add_icons(self, icon_path):
        """ Adds the icons to the folder """
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if node.bl_idname == "SN_IconNode":
                        if node.icon_source == "CUSTOM" and node.icon_file:
                            node.icon_file.reload()
                            ctx = bpy.context.copy()
                            ctx["edit_image"] = node.icon_file
                            bpy.ops.image.save_as(ctx, filepath=os.path.join(icon_path, node.icon_file.name))

    def info(self):
        """ Returns the bl_info for this addon """
        sn = bpy.context.scene.sn
        info = f"""
        bl_info = {{
            "name" : "{sn.addon_name}",
            "author" : "{sn.author}", 
            "description" : "{sn.description}",
            "blender" : {tuple(sn.blender)},
            "version" : {tuple(sn.version)},
            "location" : "{sn.location}",
            "waring" : "{sn.warning}",
            "doc_url": "{sn.doc_url}", 
            "tracker_url": "{sn.tracker_url}", 
            "category" : "{sn.category if not sn.category == 'CUSTOM' else sn.custom_category}" 
        }}
        """
        return normalize_code(info) + "\n" + "\n"

    def add_code(self, path):
        """ Creates the index file """
        bpy.context.scene.sn.is_exporting = True
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                ntree.reevaluate()
        with open(os.path.join(path, "__init__.py"), "a") as init_file:
            code = format_single_file()
            code = self.info() + code
            code = code.replace("from easybpy import", "from .easybpy import")
            # TODO format code here
            init_file.write(code)
        bpy.context.scene.sn.is_exporting = False
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                ntree.reevaluate()
        return code

    def create_files(self, path):
        """ Creates the addon files in the folder structure """
        self.add_assets(os.path.join(path, "assets"))
        self.add_icons(os.path.join(path, "icons"))
        code = self.add_code(path)
        self.add_easy_bpy(path, code)

    def create_structure(self, path):
        """ Sets up the addons folder structure at the given filepath """
        os.mkdir(path)
        baseDir = os.path.join(path, bpy.context.scene.sn.module_name)
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
        context.window_manager.progress_begin(0, 100)
        try:
            name, _ = os.path.splitext(self.filepath)
            if os.path.exists(name):
                self.report({"ERROR"}, message=f"Please delete the '{os.path.basename(name)}' folder before exporting.")
            else:
                baseDir = self.create_structure(name)
                context.window_manager.progress_update(30)
                self.create_files(baseDir)
                context.window_manager.progress_update(90)
                self.zip_addon(name)
            context.window_manager.progress_end()
        except Exception as err:
            print(err)
            context.window_manager.progress_end()
        return {"FINISHED"}

    def invoke(self, context, event):
        version = ".".join([str(i) for i in context.scene.sn.version])
        self.filepath = f"{context.scene.sn.module_name}_{version}.blend"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}