import bpy

from .....sockets.spec import String
from ....base_node import ScriptingBaseNode


class SNA_Node_CombineStrings(ScriptingBaseNode, bpy.types.Node):
    """Join strings with a separator between them."""

    bl_idname = "SNA_Node_CombineStrings"
    bl_label = "Combine Strings"
    sn_inputs = [
        String("separator", "Separator"),
        String("first", "String"),
        String("string", "String", dynamic=True),
    ]
    sn_outputs = [String("combined", "Combined")]

    def emit(self, ctx):
        strings = [ctx.input("first")] + ctx.inputs("string")
        ctx.output("combined", f"{ctx.input('separator')}.join([{', '.join(strings)}])")
