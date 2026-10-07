import bpy

from .....sockets.spec import Boolean, Interface
from ....base_node import ScriptingBaseNode


class SNA_Node_LayoutState(ScriptingBaseNode, bpy.types.Node):
    """Enable, deactivate or highlight the following elements of the layout."""

    bl_idname = "SNA_Node_LayoutState"
    bl_label = "Set Layout State"
    sn_inputs = [
        Interface(),
        Boolean("enabled", "Enabled", default=True),
        Boolean("active", "Active", default=True),
        Boolean("alert", "Alert", default=False),
    ]
    sn_outputs = [Interface("next")]

    def emit(self, ctx):
        layout = ctx.layout
        ctx.code(f"""
            {layout}.enabled = {ctx.input("enabled")}
            {layout}.active = {ctx.input("active")}
            {layout}.alert = {ctx.input("alert")}
            {ctx.flow("next")}
        """)
