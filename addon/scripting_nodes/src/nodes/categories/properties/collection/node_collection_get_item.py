import bpy

from .....core.context import NodeError
from .....sockets.spec import BlendData, Integer
from ....base_node import ScriptingBaseNode


class SNA_Node_CollectionGetItem(ScriptingBaseNode, bpy.types.Node):
    """The item at an index of a collection property."""

    bl_idname = "SNA_Node_CollectionGetItem"
    bl_label = "Collection Get Item"
    sn_inputs = [BlendData("collection", "Collection"), Integer("index", "Index")]
    sn_outputs = [BlendData("item", "Item")]

    def emit(self, ctx):
        if not ctx.is_linked("collection"):
            raise NodeError("Connect a collection")
        ctx.output("item", f"{ctx.input('collection')}[{ctx.input('index')}]")
