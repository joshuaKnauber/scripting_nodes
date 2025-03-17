from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
import bpy


class SNA_Node_VectorMath(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_VectorMath"
    bl_label = "Vector Math"

    SINGLE_INPUT_OPS = ["NORMALIZE", "LENGTH"]

    OPERATIONS_NEEDING_MATH = ["NORMALIZE", "LENGTH", "DISTANCE"]

    OPERATIONS = [
        ("ADD", "Add", "Vector addition (A + B)"),
        ("SUBTRACT", "Subtract", "Vector subtraction (A - B)"),
        ("MULTIPLY", "Multiply", "Component-wise multiplication (A * B)"),
        ("DIVIDE", "Divide", "Component-wise division (A / B)"),
        ("CROSS", "Cross Product", "Vector cross product (A × B), for 3D vectors only"),
        ("DOT", "Dot Product", "Vector dot product (A · B), outputs a float"),
        ("NORMALIZE", "Normalize", "Normalize vector A to unit length, B is ignored"),
        ("LENGTH", "Length", "Length of vector A, B is ignored, outputs a float"),
        ("DISTANCE", "Distance", "Distance between vectors A and B, outputs a float"),
    ]

    operation: bpy.props.EnumProperty(
        items=OPERATIONS,
        name="Operation",
        default="ADD",
        update=lambda self, context: self.update_operation(),
    )

    dimension: bpy.props.EnumProperty(
        items=[
            ("2", "Vec2", "Two-dimensional vector"),
            ("3", "Vec3", "Three-dimensional vector"),
            ("4", "Vec4", "Four-dimensional vector (with w component)"),
        ],
        name="Dimensions",
        default="3",
        update=lambda self, context: self.update_dimension(),
    )

    def update_operation(self):
        if self.operation in ["DOT", "LENGTH", "DISTANCE"]:
            if self.outputs[0].bl_idname != "ScriptingFloatSocket":
                update_socket_type(self.outputs[0], "ScriptingFloatSocket")
        else:
            if self.outputs[0].bl_idname != "ScriptingVectorSocket":
                update_socket_type(self.outputs[0], "ScriptingVectorSocket")

        self.outputs[0].dimension = self.dimension

        # Force Vec3 for cross product
        if self.operation == "CROSS" and self.dimension != "3":
            self.dimension = "3"

        self.update_socket_visibility()
        self.update_all_socket_dimensions()
        self._generate()

    def update_dimension(self):
        if self.operation == "CROSS" and self.dimension != "3":
            self.dimension = "3"
            return
        self.update_all_socket_dimensions()
        self._generate()

    def update_all_socket_dimensions(self):
        for socket in self.inputs:
            socket.dimension = self.dimension
        for socket in self.outputs:
            socket.dimension = self.dimension

    def update_socket_visibility(self):
        # Hide the second input socket based on the operation
        self.inputs[1].hide = self.operation in self.SINGLE_INPUT_OPS

    def on_create(self):
        self.add_input("ScriptingVectorSocket", "A")
        self.add_input("ScriptingVectorSocket", "B")
        self.add_output("ScriptingVectorSocket", "Result")
        self.update_socket_visibility()
        self.update_all_socket_dimensions()

    def draw(self, context, layout):
        layout = layout.column()
        layout.prop(self, "operation", text="")
        if self.operation != "CROSS" and any(
            not socket.is_linked for socket in self.inputs
        ):
            layout.prop(self, "dimension", text="")

    def generate(self):
        if self.operation in self.OPERATIONS_NEEDING_MATH:
            self.code_global = "import math"
        else:
            self.code_global = ""

        a = self.inputs["A"].eval()
        dim = int(self.dimension)

        if self.operation == "NORMALIZE":
            self.outputs[0].code = (
                f"tuple(v / math.sqrt(sum(x*x for x in {a})) for v in {a})"
            )

        elif self.operation == "LENGTH":
            self.outputs[0].code = f"math.sqrt(sum(x*x for x in {a}))"

        elif self.operation == "ADD":
            self.outputs[0].code = (
                f"tuple({a}[i] + {self.inputs['B'].eval()}[i] for i in range({dim}))"
            )

        elif self.operation == "SUBTRACT":
            self.outputs[0].code = (
                f"tuple({a}[i] - {self.inputs['B'].eval()}[i] for i in range({dim}))"
            )

        elif self.operation == "MULTIPLY":
            self.outputs[0].code = (
                f"tuple({a}[i] * {self.inputs['B'].eval()}[i] for i in range({dim}))"
            )

        elif self.operation == "DIVIDE":
            self.outputs[0].code = (
                f"tuple({a}[i] / {self.inputs['B'].eval()}[i] for i in range({dim}))"
            )

        elif self.operation == "CROSS":
            b = self.inputs["B"].eval()
            self.outputs[0].code = (
                f"({a}[1] * {b}[2] - {a}[2] * {b}[1], "
                f"{a}[2] * {b}[0] - {a}[0] * {b}[2], "
                f"{a}[0] * {b}[1] - {a}[1] * {b}[0])"
            )

        elif self.operation == "DOT":
            self.outputs[0].code = (
                f"sum({a}[i] * {self.inputs['B'].eval()}[i] for i in range({dim}))"
            )

        elif self.operation == "DISTANCE":
            b = self.inputs["B"].eval()
            self.outputs[0].code = (
                f"math.sqrt(sum(({a}[i] - {b}[i])**2 for i in range({dim})))"
            )
