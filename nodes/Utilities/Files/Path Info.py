import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_PathInfoNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PathInfoNode"
    bl_label = "Path Info"
    node_color = "STRING"

    def on_create(self, context):
        self.add_string_input("Path").subtype = "FILE_PATH"
        self.add_boolean_output("Path Exists")
        self.add_boolean_output("Is Directory")
        self.add_string_output("Parent Name")
        self.add_string_output("Base Name")
        self.add_string_output("Extension")

    def evaluate(self, context):
        self.code_import = "import os"
        self.outputs['Path Exists'].python_value = f"os.path.exists({self.inputs['Path'].python_value})"
        self.outputs['Is Directory'].python_value = f"os.path.isdir({self.inputs['Path'].python_value})"
        self.outputs['Parent Name'].python_value = f"os.path.dirname({self.inputs['Path'].python_value})"
        self.outputs['Base Name'].python_value = f"os.path.basename({self.inputs['Path'].python_value})"
        self.outputs['Extension'].python_value = f"os.path.splitext({self.inputs['Path'].python_value})[1]"