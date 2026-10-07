import bpy

from ....sockets.spec import Float, Integer
from ...base_node import ScriptingBaseNode


class SNA_Node_Clamp(ScriptingBaseNode, bpy.types.Node):
    """Limit a value to a range."""

    bl_idname = "SNA_Node_Clamp"
    bl_label = "Clamp"
    sn_inputs = [Float("value", "Value"), Float("min", "Min"), Float("max", "Max")]
    sn_outputs = [Float("result", "Float Result"), Integer("int", "Integer Result")]

    def emit(self, ctx):
        value, low, high = ctx.input("value"), ctx.input("min"), ctx.input("max")
        result = f"max({low}, min({high}, {value}))"
        ctx.output("result", result)
        ctx.output("int", f"int({result})")
