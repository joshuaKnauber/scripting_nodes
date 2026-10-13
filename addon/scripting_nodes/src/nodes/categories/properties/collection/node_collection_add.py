import bpy

from .....core.context import NodeError
from .....blend_data.rna import blend_data_spec
from .....sockets.data.socket_blend_data import linked_rna_type
from .....sockets.spec import BlendData, Flow
from ....base_node import ScriptingBaseNode


class SNA_Node_CollectionAdd(ScriptingBaseNode, bpy.types.Node):
    """Append a new item to a collection property."""

    bl_idname = "SNA_Node_CollectionAdd"
    bl_label = "Collection Add"
    sn_inputs = [Flow(), BlendData("collection", "Collection", collection=True)]
    sn_outputs = [Flow("next"), BlendData("new_item", "New Item")]

    def socket_specs(self):
        # items have the type of the connected collection's items
        item_type, _ = linked_rna_type(self.socket("collection"))
        return self.sn_inputs, [
            Flow("next"),
            blend_data_spec("new_item", "New Item", item_type),
        ]

    def emit(self, ctx):
        if not ctx.is_linked("collection"):
            raise NodeError("Connect a collection")
        item = ctx.var("item")
        ctx.output("new_item", item)
        ctx.code(f"""
            {item} = {ctx.input("collection")}.add()
            {ctx.flow("next")}
        """)
