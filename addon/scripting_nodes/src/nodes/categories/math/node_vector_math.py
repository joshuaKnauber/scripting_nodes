import bpy

from ....sockets.spec import Float, Vector
from ...base_node import ScriptingBaseNode

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

COMPONENT_WISE = {"ADD": "+", "SUBTRACT": "-", "MULTIPLY": "*", "DIVIDE": "/"}
SINGLE_INPUT = {"NORMALIZE", "LENGTH"}
FLOAT_RESULT = {"DOT", "LENGTH", "DISTANCE"}


class SNA_Node_VectorMath(ScriptingBaseNode, bpy.types.Node):
    """Math with 2 to 4 component vectors."""

    bl_idname = "SNA_Node_VectorMath"
    bl_label = "Vector Math"

    operation: bpy.props.EnumProperty(items=OPERATIONS, name="Operation", default="ADD")
    dimension: bpy.props.EnumProperty(
        items=[
            ("2", "Vec2", "Two-dimensional vector"),
            ("3", "Vec3", "Three-dimensional vector"),
            ("4", "Vec4", "Four-dimensional vector (with w component)"),
        ],
        name="Dimensions",
        default="3",
    )

    @property
    def size(self):
        """Vector size in use (the cross product only exists in 3D)."""
        return 3 if self.operation == "CROSS" else int(self.dimension)

    def socket_specs(self):
        inputs = [
            Vector("a", "A", dimension=self.size),
            Vector(
                "b",
                "B",
                dimension=self.size,
                enabled=self.operation not in SINGLE_INPUT,
            ),
        ]
        if self.operation in FLOAT_RESULT:
            result = Float("result", "Result")
        else:
            result = Vector("result", "Result", dimension=self.size)
        return inputs, [result]

    def draw(self, context, layout):
        layout = layout.column()
        layout.prop(self, "operation", text="")
        if self.operation != "CROSS":
            layout.prop(self, "dimension", text="")

    def emit(self, ctx):
        a = ctx.input("a")
        b = ctx.input("b") if self.operation not in SINGLE_INPUT else None
        dims = f"range({self.size})"

        if self.operation in COMPONENT_WISE:
            op = COMPONENT_WISE[self.operation]
            result = f"tuple({a}[i] {op} {b}[i] for i in {dims})"
        elif self.operation == "CROSS":
            result = (
                f"({a}[1] * {b}[2] - {a}[2] * {b}[1], "
                f"{a}[2] * {b}[0] - {a}[0] * {b}[2], "
                f"{a}[0] * {b}[1] - {a}[1] * {b}[0])"
            )
        elif self.operation == "DOT":
            result = f"sum({a}[i] * {b}[i] for i in {dims})"
        elif self.operation == "NORMALIZE":
            ctx.imports("import math")
            result = f"tuple(v / math.sqrt(sum(x * x for x in {a})) for v in {a})"
        elif self.operation == "LENGTH":
            ctx.imports("import math")
            result = f"math.sqrt(sum(x * x for x in {a}))"
        else:  # DISTANCE
            ctx.imports("import math")
            result = f"math.sqrt(sum(({a}[i] - {b}[i]) ** 2 for i in {dims}))"
        ctx.output("result", result)
