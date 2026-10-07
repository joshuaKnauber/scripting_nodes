import bpy

from .....core.context import NodeError
from .....sockets.spec import BlendData, Flow, Integer
from ....base_node import ScriptingBaseNode


class SNA_Node_CollectionRemove(ScriptingBaseNode, bpy.types.Node):
    """Remove the item at an index from a collection property."""

    bl_idname = "SNA_Node_CollectionRemove"
    bl_label = "Collection Remove"
    sn_inputs = [
        Flow(),
        BlendData("collection", "Collection"),
        Integer("index", "Index"),
    ]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        if not ctx.is_linked("collection"):
            raise NodeError("Connect a collection")
        ctx.code(f"""
            {ctx.input("collection")}.remove({ctx.input("index")})
            {ctx.flow("next")}
        """)
