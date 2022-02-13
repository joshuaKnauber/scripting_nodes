import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IsInListNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IsInListNode"
    bl_label = "Is In List"
    node_color = "LIST"

    def on_create(self, context):
        self.add_list_input()
        self.add_data_input("Element")
        self.add_boolean_output("Is In List")

    def evaluate(self, context):
        self.outputs[0].python_value = f"{self.inputs[1].python_value} in {self.inputs[0].python_value}"