import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ListDirectoryFilesNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ListDirectoryFilesNode"
    bl_label = "List Directory Files"
    node_color = "STRING"

    def on_create(self, context):
        self.add_string_input("Path").subtype = "FILE_PATH"
        self.add_list_output("Files + Directories")

    def evaluate(self, context):
        self.code_import = "import os"
        self.outputs[0].python_value = f"os.listdir({self.inputs['Path'].python_value})"