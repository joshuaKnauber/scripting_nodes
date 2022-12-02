import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_IndexOfElementNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IndexOfElementNode"
    bl_label = "Index Of List Element"
    node_color = "LIST"

    def on_create(self, context):
        self.add_list_input()
        self.add_data_input("Element")
        self.add_integer_output("Index")

    def evaluate(self, context):
        self.outputs[0].python_value = f"{self.inputs[0].python_value}.index({self.inputs[1].python_value})"