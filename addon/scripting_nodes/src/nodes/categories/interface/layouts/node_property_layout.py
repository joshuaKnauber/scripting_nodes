import bpy

from .....sockets.spec import Boolean, Interface
from ....base_node import ScriptingBaseNode


class SNA_Node_PropertyLayout(ScriptingBaseNode, bpy.types.Node):
    """How the following properties are laid out (label split, decorators)."""

    bl_idname = "SNA_Node_PropertyLayout"
    bl_label = "Set Property Layout"
    sn_inputs = [
        Interface(),
        Boolean("decorate", "Decorated", default=False),
        Boolean("split", "Split", default=False),
    ]
    sn_outputs = [Interface("next")]

    def emit(self, ctx):
        layout = ctx.layout
        ctx.code(f"""
            {layout}.use_property_decorate = {ctx.input("decorate")}
            {layout}.use_property_split = {ctx.input("split")}
            {ctx.flow("next")}
        """)
