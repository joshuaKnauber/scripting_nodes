import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_AbsolutePathNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_AbsolutePathNode"
    bl_label = "Make Path Absolute"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("Relative").subtype = "FILE_PATH"
        self.add_string_output("Absolute").subtype = "FILE_PATH"

    def evaluate(self, context):
        self.outputs["Absolute"].python_value = f"bpy.path.abspath({self.inputs[0].python_value})"