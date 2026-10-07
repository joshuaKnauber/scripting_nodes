import bpy

from ....sockets.spec import Float, Integer
from ...base_node import ScriptingBaseNode


class SNA_Node_RoundFloat(ScriptingBaseNode, bpy.types.Node):
    """Round a number to a number of decimals."""

    bl_idname = "SNA_Node_RoundFloat"
    bl_label = "Round Float"
    sn_inputs = [Float("float", "Float"), Integer("decimals", "Decimals")]
    sn_outputs = [Float("result", "Rounded Float")]
    sn_header_props = ("round_up_or_down",)

    round_up_or_down: bpy.props.EnumProperty(
        items=[
            ("UP", "Up", "Round up"),
            ("DOWN", "Down", "Round down"),
            ("NEAREST", "Nearest", "Round to the nearest float value"),
        ],
        name="Round",
        default="NEAREST",
    )

    def emit(self, ctx):
        value, decimals = ctx.input("float"), ctx.input("decimals")
        if self.round_up_or_down == "NEAREST":
            ctx.output("result", f"round({value}, {decimals})")
            return
        ctx.imports("import math")
        function = "ceil" if self.round_up_or_down == "UP" else "floor"
        factor = f"(10 ** {decimals})"
        ctx.output("result", f"math.{function}({value} * {factor}) / {factor}")
