import bpy

from .....sockets.spec import Boolean, Interface, String
from ....base_node import ScriptingBaseNode


class SNA_Node_Row(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Row"
    bl_label = "Row"
    sn_inputs = [Interface(), Boolean("align", "Align"), String("heading", "Heading")]
    sn_outputs = [Interface("content", "Row"), Interface("next", "After")]

    def emit(self, ctx):
        row = ctx.var("row")
        ctx.code(f"""
            {row} = {ctx.layout}.row(align={ctx.input("align")}, heading={ctx.input("heading")})
            {ctx.flow("content", layout=row)}
            {ctx.flow("next")}
        """)
