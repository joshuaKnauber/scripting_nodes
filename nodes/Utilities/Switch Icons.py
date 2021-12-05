import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SwitchIconNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SwitchIconNode"
    bl_label = "Switch Icons"
    node_color = "ICON"

    def on_create(self, context):
        self.add_boolean_input("Switch")
        self.add_icon_input("Icon 1")
        self.add_icon_input("Icon 2")
        self.add_icon_output("Icon")

    def evaluate(self, context):
        self.outputs[0].python_value = f"{self.inputs[2].python_value} if {self.inputs[0].python_value} else {self.inputs[1].python_value}"