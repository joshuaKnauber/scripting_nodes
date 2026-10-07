import bpy

from .....core.context import NodeError
from .....blend_data.rna import blend_data_spec
from .....sockets.data.socket_blend_data import linked_rna_type
from .....sockets.spec import BlendData, Integer
from ....base_node import ScriptingBaseNode


class SNA_Node_CollectionGetItem(ScriptingBaseNode, bpy.types.Node):
    """The item at an index of a collection property."""

    bl_idname = "SNA_Node_CollectionGetItem"
    bl_label = "Collection Get Item"
    sn_inputs = [
        BlendData("collection", "Collection", collection=True),
        Integer("index", "Index"),
    ]
    sn_outputs = [BlendData("item", "Item")]

    def socket_specs(self):
        # items have the type of the connected collection's items
        item_type, _ = linked_rna_type(self.socket("collection"))
        return self.sn_inputs, [blend_data_spec("item", "Item", item_type)]

    def emit(self, ctx):
        if not ctx.is_linked("collection"):
            raise NodeError("Connect a collection")
        ctx.output("item", f"{ctx.input('collection')}[{ctx.input('index')}]")
