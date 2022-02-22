import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IndexListNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IndexListNode"
    bl_label = "Index List"
    node_color = "LIST"

    def on_create(self, context):
        self.add_list_input()
        self.add_integer_input("Index")
        self.add_data_output().changeable = True

    def evaluate(self, context):
        self.outputs[0].python_value = f"{self.inputs[0].python_value}[{self.inputs[1].python_value}]"