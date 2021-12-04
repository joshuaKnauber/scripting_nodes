import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_PathExistsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PathExistsNode"
    bl_label = "Path Exists"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("Path").subtype = "FILE_PATH"
        self.add_boolean_output("Path Exists")

    def evaluate(self, context):
        self.code_import = "import os"
        self.outputs[0].python_value = f"os.path.exists({self.inputs['Path'].python_value})"