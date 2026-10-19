import bpy

from ....sockets.spec import Float, Integer
from ...base_node import ScriptingBaseNode

OPERATIONS = {
    "ADD": ("Add", "+"),
    "SUBTRACT": ("Subtract", "-"),
    "MULTIPLY": ("Multiply", "*"),
    "DIVIDE": ("Divide", "/"),
    "POWER": ("Power", "**"),
    "MODULO": ("Modulo", "%"),
}


class SNA_Node_Math(ScriptingBaseNode, bpy.types.Node):
    """Calculate with numbers: add, multiply, round, compare and more."""

    bl_idname = "SNA_Node_Math"
    bl_label = "Math"
    sn_inputs = [Float("a", "A"), Float("b", "B")]
    sn_outputs = [Float("result", "Float Result"), Integer("int", "Integer Result")]
    sn_header_props = ("operation",)

    operation: bpy.props.EnumProperty(
        name="Operation",
        items=[(key, label, label) for key, (label, _) in OPERATIONS.items()],
    )

    def emit(self, ctx):
        operator = OPERATIONS[self.operation][1]
        result = f"{ctx.input('a')} {operator} {ctx.input('b')}"
        ctx.output("result", result)
        integers = all(ctx.is_integer(key) for key in ("a", "b"))
        if integers and operator not in ("/", "**"):
            ctx.output("int", result)  # already one
        else:
            ctx.output("int", f"int({result})")
