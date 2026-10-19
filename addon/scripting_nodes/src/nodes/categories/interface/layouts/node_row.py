import bpy

from .....sockets.spec import Boolean, Interface, String
from ....base_node import ScriptingBaseNode


class SNA_Node_Row(ScriptingBaseNode, bpy.types.Node):
    """Draw the connected UI next to each other."""

    bl_idname = "SNA_Node_Row"
    bl_label = "Row"
    sn_inputs = [Interface(), Boolean("align", "Align"), String("heading", "Heading")]
    sn_outputs = [Interface("content", "Row"), Interface("next", "After")]

    def emit(self, ctx):
        row = ctx.var("row")
        ctx.code(f"""
            {row} = {ctx.layout}.row({ctx.args(ctx.keyword("align", "align", False), ctx.keyword("heading", "heading", ""))})
            {ctx.flow("content", layout=row, horizontal=True)}
            {ctx.flow("next")}
        """)
