from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Math(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Math"
    bl_label = "Math"

    OPERATIONS = {
        "ADD": "+",
        "SUBTRACT": "-",
        "MULTIPLY": "*",
        "DIVIDE": "/",
        "POWER": "**",
        "MODULO": "%",
    }

    operation: bpy.props.EnumProperty(
        items=[
            ("ADD", "Add", "Addition"),
            ("SUBTRACT", "Subtract", "Subtraction"),
            ("MULTIPLY", "Multiply", "Multiplication"),
            ("DIVIDE", "Divide", "Division"),
            ("POWER", "Power", "Power"),
            ("MODULO", "Modulo", "Modulo"),
        ],
        name="Operation",
        default="ADD",
        update=lambda self, context: self._generate(),
    )

    def on_create(self):
        self.add_input("ScriptingFloatSocket", "A")
        self.add_input("ScriptingFloatSocket", "B")
        self.add_output("ScriptingFloatSocket", "Float Result")
        self.add_output("ScriptingIntegerSocket", "Integer Result")

    def draw(self, context, layout):
        layout.prop(self, "operation", text="")

    def generate(self):
        a = self.inputs["A"].eval()
        b = self.inputs["B"].eval()

        result = f"({a} {self.OPERATIONS[self.operation]} {b})"

        self.outputs["Float Result"].code = result
        self.outputs["Integer Result"].code = f"int({result})"
