import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ListLengthNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ListLengthNode"
    bl_label = "List Length"
    node_color = "LIST"

    def on_create(self, context):
        self.add_list_input()
        self.add_integer_output("Length")

    def evaluate(self, context):
        self.outputs[0].python_value = f"len({self.inputs[0].python_value})"