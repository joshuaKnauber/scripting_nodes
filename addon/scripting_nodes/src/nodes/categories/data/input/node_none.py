import bpy

from .....sockets.spec import Data
from ....base_node import ScriptingBaseNode


class SNA_Node_None(ScriptingBaseNode, bpy.types.Node):
    """The value None."""

    bl_idname = "SNA_Node_None"
    bl_label = "None"
    sn_outputs = [Data("value", "None")]

    def emit(self, ctx):
        ctx.output("value", "None")
