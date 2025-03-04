from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
import bpy


class SNA_Node_Math(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Math"
    bl_label = "Math"

    # Math operations with their corresponding Python operators
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

    as_integer: bpy.props.BoolProperty(
        name="As Integer",
        description="Output the result as an integer",
        default=False,
        update=lambda self, context: self.update_output_socket(context),
    )

    def update_output_socket(self, context):
        target_socket = (
            "ScriptingIntegerSocket" if self.as_integer else "ScriptingFloatSocket"
        )
        if self.outputs[0].bl_idname != target_socket:
            update_socket_type(self.outputs[0], target_socket)
        self._generate()

    def on_create(self):
        self.add_input("ScriptingFloatSocket", "A")
        self.add_input("ScriptingFloatSocket", "B")
        self.add_output("ScriptingFloatSocket", "Result")

    def draw(self, context, layout):
        layout = layout.column(align=True)
        layout.prop(self, "operation", text="")
        layout.prop(self, "as_integer", text="Integer Output")

    def generate(self):
        a = self.inputs["A"].eval()
        b = self.inputs["B"].eval()

        result = f"{a} {self.OPERATIONS[self.operation]} {b}"

        if self.as_integer:
            result = f"int({result})"

        if len(self.outputs) > 0:
            self.outputs[0].code = result
