import bpy

from .....core.context import NodeError
from .....sockets.spec import BlendData, Flow
from ....base_node import ScriptingBaseNode


class SNA_Node_CollectionClear(ScriptingBaseNode, bpy.types.Node):
    """Remove all items from a collection property."""

    bl_idname = "SNA_Node_CollectionClear"
    bl_label = "Collection Clear"
    sn_inputs = [Flow(), BlendData("collection", "Collection")]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        if not ctx.is_linked("collection"):
            raise NodeError("Connect a collection")
        ctx.code(f"""
            {ctx.input("collection")}.clear()
            {ctx.flow("next")}
        """)
