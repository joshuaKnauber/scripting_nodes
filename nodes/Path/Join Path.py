import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_JoinPathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_JoinPathNode"
    bl_label = "Join Path"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("Basepath").subtype = "DIR_PATH"
        self.add_dynamic_string_input("Path Part")
        self.add_string_output("Path").subtype = "FILE_PATH"

    def evaluate(self, context):
        self.code_import = "import os"
        self.outputs[0].python_value = f"os.path.join({self.inputs[0].python_value},{','.join([inp.python_value for inp in self.inputs[1:-1]])})"