import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ClampNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ClampNode"
    bl_label = "Clamp"
    node_color = "FLOAT"

    def on_create(self, context):
        self.add_float_input("Value")
        self.add_float_input("Min").can_be_disabled = True
        self.add_float_input("Max").can_be_disabled = True
        self.add_float_output("Float Result")
        self.add_integer_output("Integer Result")

    def evaluate(self, context):
        smallest = self.inputs["Min"].python_value
        largest = self.inputs["Max"].python_value

        if self.inputs["Min"].disabled:
            smallest = self.inputs["Value"].python_value
        if self.inputs["Max"].disabled:
            largest = self.inputs["Value"].python_value

        self.outputs[0].python_value = f"float(max({smallest}, min({self.inputs[0].python_value}, {largest})))"
        self.outputs[1].python_value = f"int(max({smallest}, min({self.inputs[0].python_value}, {largest})))"