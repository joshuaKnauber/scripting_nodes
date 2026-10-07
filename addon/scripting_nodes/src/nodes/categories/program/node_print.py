import bpy

from ....sockets.spec import Flow, String
from ...base_node import ScriptingBaseNode


class SNA_Node_Print(ScriptingBaseNode, bpy.types.Node):
    """Print a message (also shown in the node editor while developing)."""

    bl_idname = "SNA_Node_Print"
    bl_label = "Print"
    sn_inputs = [Flow(), String("text", "Text")]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.helper("sn_print")}({ctx.input("text")})
            {ctx.flow("next")}
        """)
