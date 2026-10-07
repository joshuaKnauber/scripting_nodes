import bpy

from .....sockets.spec import Boolean, Interface, String
from ....base_node import ScriptingBaseNode


class SNA_Node_Column(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Column"
    bl_label = "Column"
    sn_inputs = [Interface(), Boolean("align", "Align"), String("heading", "Heading")]
    sn_outputs = [Interface("content", "Column"), Interface("next", "After")]

    def emit(self, ctx):
        col = ctx.var("col")
        ctx.code(f"""
            {col} = {ctx.layout}.column(align={ctx.input("align")}, heading={ctx.input("heading")})
            {ctx.flow("content", layout=col)}
            {ctx.flow("next")}
        """)
