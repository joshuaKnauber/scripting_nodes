import bpy

from .....core.context import NodeError
from .....sockets.spec import BlendData, Flow
from ....base_node import ScriptingBaseNode


class SNA_Node_CollectionAdd(ScriptingBaseNode, bpy.types.Node):
    """Append a new item to a collection property."""

    bl_idname = "SNA_Node_CollectionAdd"
    bl_label = "Collection Add"
    sn_inputs = [Flow(), BlendData("collection", "Collection")]
    sn_outputs = [Flow("next"), BlendData("new_item", "New Item")]

    def emit(self, ctx):
        if not ctx.is_linked("collection"):
            raise NodeError("Connect a collection")
        item = ctx.var("item")
        ctx.output("new_item", item)
        ctx.code(f"""
            {item} = {ctx.input("collection")}.add()
            {ctx.flow("next")}
        """)
