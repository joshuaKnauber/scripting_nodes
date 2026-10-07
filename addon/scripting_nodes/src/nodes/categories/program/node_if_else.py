import bpy

from ....sockets.spec import Boolean, Flow
from ...base_node import ScriptingBaseNode


class SNA_Node_IfElse(ScriptingBaseNode, bpy.types.Node):
    """Run one of two branches depending on a condition."""

    bl_idname = "SNA_Node_IfElse"
    bl_label = "If/Else"
    sn_inputs = [Flow(), Boolean("condition", "Condition")]
    sn_outputs = [Flow("then", "Then"), Flow("else", "Else"), Flow("next", "Finally")]

    def emit(self, ctx):
        ctx.code(f"""
            if {ctx.input("condition")}:
                {ctx.flow("then")}
            else:
                {ctx.flow("else")}
            {ctx.flow("next")}
        """)
