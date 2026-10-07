import bpy

from ....sockets.spec import Boolean, Data
from ...base_node import ScriptingBaseNode


class SNA_Node_Compare(ScriptingBaseNode, bpy.types.Node):
    """Compare two values."""

    bl_idname = "SNA_Node_Compare"
    bl_label = "Compare"
    sn_inputs = [Data("a", "A"), Data("b", "B")]
    sn_outputs = [Boolean("result", "Result")]
    sn_header_props = ("comparison_type",)

    comparison_type: bpy.props.EnumProperty(
        items=[
            ("==", "=", "Equal to"),
            ("!=", "≠", "Not equal to"),
            ("<", "<", "Less than"),
            ("<=", "≤", "Less than or equal to"),
            (">", ">", "Greater than"),
            (">=", "≥", "Greater than or equal to"),
        ],
        name="Comparison Type",
    )

    def emit(self, ctx):
        a, b = ctx.input("a"), ctx.input("b")
        ctx.output("result", f"{a} {self.comparison_type} {b}")
