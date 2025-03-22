from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_MapRange(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_MapRange"
    bl_label = "Map Range"

    def on_create(self):
        self.add_input("ScriptingFloatSocket", "Value")
        self.add_input("ScriptingFloatSocket", "Old Min").value = 0
        self.add_input("ScriptingFloatSocket", "Old Max").value = 1
        self.add_input("ScriptingFloatSocket", "New Min").value = 0
        self.add_input("ScriptingFloatSocket", "New Max").value = 10
        self.add_output("ScriptingFloatSocket", "Float Result")
        self.add_output("ScriptingIntegerSocket", "Integer Result")

    def generate(self):
        value = self.inputs["Value"].eval()
        old_min = self.inputs["Old Min"].eval()
        old_max = self.inputs["Old Max"].eval()
        new_min = self.inputs["New Min"].eval()
        new_max = self.inputs["New Max"].eval()

        float_result = f"({value} - {old_min}) * ({new_max} - {new_min}) / ({old_max} - {old_min}) + {new_min}"

        self.outputs["Float Result"].code = float_result
        self.outputs["Integer Result"].code = f"int({float_result})"
