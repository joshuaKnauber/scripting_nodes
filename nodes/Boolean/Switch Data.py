import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SwitchDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SwitchDataNode"
    bl_label = "Switch Data"
    node_color = "DEFAULT"

    def on_create(self, context):
        self.add_boolean_input("Switch")
        self.add_data_input("Data 1")
        self.add_data_input("Data 2")
        self.add_data_output("Data")

    def evaluate(self, context):
        self.outputs[0].python_value = f"({self.inputs[2].python_value} if {self.inputs[0].python_value} else {self.inputs[1].python_value})"