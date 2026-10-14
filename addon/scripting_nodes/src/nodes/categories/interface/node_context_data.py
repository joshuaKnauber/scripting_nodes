import bpy

from ....core.context import NodeError
from ....sockets.spec import BlendData, Interface, String
from ...base_node import ScriptingBaseNode


class SNA_Node_ContextData(ScriptingBaseNode, bpy.types.Node):
    """Give the buttons after it data in their context: an operator they run
    reads it as context.<name>, e.g. the item of the row a button is in."""

    bl_idname = "SNA_Node_ContextData"
    bl_label = "Set Context Data"
    sn_inputs = [
        Interface(),
        String("name", "Name", default="item"),
        BlendData("data", "Data"),
    ]
    sn_outputs = [Interface("next")]

    def emit(self, ctx):
        name = self.socket("name")
        if not name.is_linked and not name.value.isidentifier():
            raise NodeError("The name has to be a valid Python name")
        ctx.code(f"""
            {ctx.layout}.context_pointer_set({ctx.input("name")}, {ctx.input("data", default="None")})
            {ctx.flow("next")}
        """)
