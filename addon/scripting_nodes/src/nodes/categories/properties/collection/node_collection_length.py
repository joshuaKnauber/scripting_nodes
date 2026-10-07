import bpy

from .....core.context import NodeError
from .....sockets.spec import BlendData, Integer
from ....base_node import ScriptingBaseNode


class SNA_Node_CollectionLength(ScriptingBaseNode, bpy.types.Node):
    """Number of items in a collection property."""

    bl_idname = "SNA_Node_CollectionLength"
    bl_label = "Collection Length"
    sn_inputs = [BlendData("collection", "Collection")]
    sn_outputs = [Integer("length", "Length")]

    def emit(self, ctx):
        if not ctx.is_linked("collection"):
            raise NodeError("Connect a collection")
        ctx.output("length", f"len({ctx.input('collection')})")
