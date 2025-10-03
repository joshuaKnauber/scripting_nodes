from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Compare(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Compare"
    bl_label = "Compare"

    def update_comparison(self, context):
        self._generate()

    def on_create(self):
        self.add_input("ScriptingDataSocket", label="A")
        self.add_input("ScriptingDataSocket", label="B")
        self.add_output("ScriptingBooleanSocket", label="Result")

    comparison_types = [
        ("==", "=", "Equal to"),
        ("!=", "≠", "Not equal to"),
        ("<", "<", "Less than"),
        ("<=", "≤", "Less than or equal to"),
        (">", ">", "Greater than"),
        (">=", "≥", "Greater than or equal to"),
    ]
    comparison_type: bpy.props.EnumProperty(
        items=comparison_types, name="Comparison Type", update=update_comparison
    )

    def draw(self, context, layout):
        layout.prop(self, "comparison_type", text="")

    def generate(self):
        self.outputs[0].code = (
            f"{self.inputs[0].eval()} {self.comparison_type} {self.inputs[1].eval()}"
        )