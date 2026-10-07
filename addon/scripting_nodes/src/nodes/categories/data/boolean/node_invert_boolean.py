import bpy

from .....sockets.spec import Boolean
from ....base_node import ScriptingBaseNode


class SNA_Node_InvertBoolean(ScriptingBaseNode, bpy.types.Node):
    """True becomes False and the other way around."""

    bl_idname = "SNA_InvertBoolean"
    bl_label = "Invert Boolean"
    sn_inputs = [Boolean("boolean", "Boolean")]
    sn_outputs = [Boolean("result", "Result")]

    def emit(self, ctx):
        ctx.output("result", f"not {ctx.input('boolean')}")
