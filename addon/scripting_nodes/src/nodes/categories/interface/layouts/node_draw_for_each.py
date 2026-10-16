import bpy

from .....sockets.spec import Data, Integer, Interface, List
from ...._loop import for_each
from ....base_node import ScriptingBaseNode


class SNA_Node_DrawForEach(ScriptingBaseNode, bpy.types.Node):
    """Draw the Item flow once per item of a list or collection, e.g. a row
    per object."""

    bl_idname = "SNA_Node_DrawForEach"
    bl_label = "Draw For Each"
    sn_inputs = [Interface(), List("list", "List")]
    sn_outputs = [
        Interface("loop", "Item"),
        Interface("next", "After"),
        Data("item", "Item"),
        Integer("index", "Index"),
    ]

    def emit(self, ctx):
        header, outputs = for_each(ctx, ctx.input("list"))
        loop = ctx.flow("loop", outputs=outputs, loop=True)
        ctx.code(f"""
            {header}
                {loop}
            {ctx.flow("next")}
        """)
