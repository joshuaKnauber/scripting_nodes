from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Clamp(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Clamp"
    bl_label = "Clamp"

    def on_create(self):
        self.add_input("ScriptingFloatSocket", "Value")
        self.add_input("ScriptingFloatSocket", "Min")
        self.add_input("ScriptingFloatSocket", "Max")
        self.add_output("ScriptingFloatSocket", "Float Result")
        self.add_output("ScriptingIntegerSocket", "Integer Result")

    def generate(self):
        value = self.inputs["Value"].eval()
        min_val = self.inputs["Min"].eval()
        max_val = self.inputs["Max"].eval()

        float_result = f"max({min_val}, min({max_val}, {value}))"

        self.outputs["Float Result"].code = float_result
        self.outputs["Integer Result"].code = f"int({float_result})"
