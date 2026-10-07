import bpy

from ....sockets.spec import Float, Integer
from ...base_node import ScriptingBaseNode


class SNA_Node_MapRange(ScriptingBaseNode, bpy.types.Node):
    """Map a value from one range to another."""

    bl_idname = "SNA_Node_MapRange"
    bl_label = "Map Range"
    sn_inputs = [
        Float("value", "Value"),
        Float("old_min", "Old Min", default=0),
        Float("old_max", "Old Max", default=1),
        Float("new_min", "New Min", default=0),
        Float("new_max", "New Max", default=10),
    ]
    sn_outputs = [Float("result", "Float Result"), Integer("int", "Integer Result")]

    def emit(self, ctx):
        value = ctx.input("value")
        old_min, old_max = ctx.input("old_min"), ctx.input("old_max")
        new_min, new_max = ctx.input("new_min"), ctx.input("new_max")
        result = (
            f"({value} - {old_min}) * ({new_max} - {new_min}) "
            f"/ ({old_max} - {old_min}) + {new_min}"
        )
        ctx.output("result", result)
        ctx.output("int", f"int({result})")
