import bpy
import os
import shutil
import json
import zipfile
from bpy_extras.io_utils import ImportHelper



loaded_packages = [] # temp var for the loaded packages in a file
require_reload = False # set to true after a package is installed



class SN_OT_InstallPackage(bpy.types.Operator, ImportHelper):
    bl_idname = "sn.install_package"
    bl_label = "Install Package"
    bl_description = "Let's you install a package from a zip file"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    filter_glob: bpy.props.StringProperty( default='*.zip', options={'HIDDEN'} )
    
    def extract_zip(self):
        node_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)),"nodes")
        names = []
        with zipfile.ZipFile(self.filepath, 'r') as zip_ref:
            zip_ref.extractall(node_directory)
            names = zip_ref.namelist()
        return names
    
    def get_package_info(self):
        info_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"nodes","package_info.json")
        package_info = None
        if os.path.exists(info_path):
            with open(info_path) as info:
                package_info = json.loads(info.read())
            os.remove(info_path)
        return package_info
    
    def write_to_installed(self, new_package, extracted):
        installed_path = os.path.join(os.path.dirname(__file__),"installed.json")
        with open(installed_path,"r+") as installed:
            data = json.loads(installed.read())
            new_package["nodes"] = extracted
            data["packages"].append(new_package)
            installed.seek(0)
            installed.write(json.dumps(data,indent=4))
            installed.truncate()

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        if extension == ".zip":
            extracted_files = self.extract_zip()
            package_info = self.get_package_info()
            if not package_info:
                package_info = {
                    "name": os.path.basename(filename),
                    "author": "Unknown",
                    "description": "",
                    "version": "1.0.0",
                    "wiki": ""}
            self.write_to_installed(package_info, extracted_files)

        bpy.ops.sn.reload_packages()
        global require_reload
        require_reload = True
        return {"FINISHED"}
    
    
    
class SN_OT_ReloadPackages(bpy.types.Operator):
    bl_idname = "sn.reload_packages"
    bl_label = "Reload Packages"
    bl_description = "Reloads the installed packages list"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        global loaded_packages
        installed_path = os.path.join(os.path.dirname(__file__),"installed.json")
        with open(installed_path, "r") as installed:
            data = json.loads(installed.read())
            loaded_packages = data["packages"]
        return {"FINISHED"}



class SN_OT_UninstallPackage(bpy.types.Operator):
    bl_idname = "sn.uninstall_package"
    bl_label = "Uninstall Package"
    bl_description = "Uninstalls this package"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    index: bpy.props.IntProperty()
    
    def get_package(self):
        installed_path = os.path.join(os.path.dirname(__file__),"installed.json")
        package = None
        with open(installed_path,"r+") as installed:
            data = json.loads(installed.read())
            package = data["packages"][self.index]
            data["packages"].pop(self.index)
            installed.seek(0)
            installed.write(json.dumps(data,indent=4))
            installed.truncate()
        return package
    
    def remove_nodes(self,nodes):
        for name in nodes:
            if not "__init__" in name:
                path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"nodes",name)
                if os.path.exists(path) and not os.path.isdir(path):
                    os.remove(path)
                    
    def remove_empty_dirs(self):
        dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),"nodes")
        for file in os.listdir(dir):
            path = os.path.join(dir, file)
            if os.path.isdir(path):
                files = os.listdir(path)
                if len(files) == 0 or (len(files) == 1 and "__init__.py" in files):
                    shutil.rmtree(path)
    
    def execute(self, context):
        package = self.get_package()
        if package:
            self.remove_nodes(package["nodes"])
            self.remove_empty_dirs()
            
        bpy.ops.sn.reload_packages()
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)