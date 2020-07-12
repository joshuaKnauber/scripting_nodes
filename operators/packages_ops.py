import bpy
from bpy_extras.io_utils import ImportHelper
import os
import shutil
import zipfile
import json
from ..__init__ import reregister_node_categories


class SN_OT_InstallPackage(bpy.types.Operator, ImportHelper):
    bl_idname = "scripting_nodes.install_package"
    bl_label = "Install Package"
    bl_description = "Install a node package from a zip file"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    filter_glob: bpy.props.StringProperty( default='*.zip', options={'HIDDEN'} )
    files: bpy.props.CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)

    @classmethod
    def poll(cls, context):
        return True

    def _add_package_to_json(self, files):
        """ adds the package name and the corresponding files to the json file """
        addon_folder = os.path.dirname(os.path.dirname(__file__))

        for filename in files:
            if filename == "package_info.json":
                with open(os.path.join(addon_folder,"nodes",filename)) as package_data:
                    package_data = json.load(package_data)
                    if "name" in package_data and "description" in package_data and "nodes" in package_data and "author" in package_data:

                        with open(os.path.join(addon_folder,"installed_packages.json"),"r+") as packages:
                            packages_content = json.load(packages)
                            packages_content["packages"].append(package_data)
                            packages.seek(0)
                            packages.write(json.dumps(packages_content,indent=4))
                            packages.truncate()
                os.remove(os.path.join(addon_folder,"nodes",filename))

    def _install_package(self,filepath):
        """ installs the given filepath """
        node_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)),"nodes")
        names = []
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(node_directory)
            names = zip_ref.namelist()
            
        for file_path in names:
            init_path = os.path.join(node_directory,os.path.dirname(file_path),"__init__.py")
            if not os.path.exists(init_path):
                open(init_path, 'a').close()

        self._add_package_to_json(names)

        bpy.context.scene.sn_properties.package_installed_without_compile = True
        reregister_node_categories(names)
        self.report({"INFO"},message="Package succesfully installed")

    def execute(self, context):
        for file_element in self.files:
            _, extension = os.path.splitext(file_element.name)
            if extension == ".zip":
                filepath = os.path.join(os.path.dirname(self.filepath),file_element.name)
                self._install_package(filepath)
        return {"FINISHED"}



class SN_OT_UninstallPackage(bpy.types.Operator):
    bl_idname = "scripting_nodes.uninstall_package"
    bl_label = "Uninstall Package"
    bl_description = "Uninstalls this package"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    package_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return True

    def _remove_node_files(self):
        """ removes the node files from the addon folder """
        addon_folder = os.path.dirname(os.path.dirname(__file__))
        with open(os.path.join(addon_folder,"installed_packages.json"),"r+") as packages:
            packages_content = json.load(packages)["packages"][self.package_index]
            for node in packages_content["nodes"]:
                if not "__init__.py" in node:
                    os.remove(os.path.join(addon_folder,"nodes",node))

    def _remove_empty_folders(self):
        """ removes any remaining empty node folders """
        addon_folder = os.path.dirname(os.path.dirname(__file__))
        for directory in os.listdir(os.path.join(addon_folder,"nodes")):
            delete_path = os.path.join(os.path.join(addon_folder,"nodes",directory))
            should_delete = True
            if not directory == "__init__.py":
                for _, _, files in os.walk(delete_path):
                    for check_file in files:
                        if check_file.split(".")[-1] == "py" and not check_file == "__init__.py":
                            should_delete = False
            else:
                should_delete = False
            if should_delete and not delete_path == os.path.join(os.path.join(addon_folder,"nodes","__pycache__")):
                shutil.rmtree(delete_path)

    def _remove_package_from_json(self):
        """ removes the package from the json file """
        addon_folder = os.path.dirname(os.path.dirname(__file__))
        with open(os.path.join(addon_folder,"installed_packages.json"),"r+") as packages:
            packages_content = json.load(packages)
            packages_content["packages"].pop(self.package_index)
            packages.seek(0)
            packages.write(json.dumps(packages_content,indent=4))
            packages.truncate()

    def execute(self, context):
        self._remove_node_files()
        self._remove_empty_folders()
        self._remove_package_from_json()
        self.report({"INFO"},message="Uninstalled package successfully!")
        context.scene.sn_properties.package_uninstalled_without_compile = True
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)