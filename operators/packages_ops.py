import bpy
from bpy_extras.io_utils import ImportHelper
import os
import zipfile
from ..__init__ import reregister_node_categories


class SN_OT_InstallPackage(bpy.types.Operator, ImportHelper):
    bl_idname = "scripting_nodes.install_package"
    bl_label = "Install Package"
    bl_description = "Install a node package from a zip file"
    bl_options = {"REGISTER"}

    filter_glob: bpy.props.StringProperty( default='*.zip', options={'HIDDEN'} )
    files: bpy.props.CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)

    @classmethod
    def poll(cls, context):
        return True

    def _install_package(self,filepath):
        """ installs the given filepath """
        node_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)),"nodes")
        names = []
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(node_directory)
            names = zip_ref.namelist()
        reregister_node_categories(names)

    def execute(self, context):
        for file_element in self.files:
            _, extension = os.path.splitext(file_element.name)
            if extension == ".zip":
                filepath = os.path.join(os.path.dirname(self.filepath),file_element.name)
                self._install_package(filepath)
        return {"FINISHED"}
