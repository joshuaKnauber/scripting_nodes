import bpy

from .....sockets.spec import Boolean
from ....base_node import ScriptingBaseNode


class SNA_Node_BooleanMath(ScriptingBaseNode, bpy.types.Node):
    """Combine two booleans with and/or."""

    bl_idname = "SNA_BooleanMath"
    bl_label = "Boolean Math"
    sn_inputs = [Boolean("a", "Boolean"), Boolean("b", "Boolean")]
    sn_outputs = [Boolean("result", "Result")]
    sn_header_props = ("comparison",)

    comparison: bpy.props.EnumProperty(
        items=[
            ("AND", "And", ""),
            ("OR", "Or", ""),
        ],
        name="Comparison",
        default="AND",
    )

    def emit(self, ctx):
        operator = self.comparison.lower()
        ctx.output("result", f"{ctx.input('a')} {operator} {ctx.input('b')}")
