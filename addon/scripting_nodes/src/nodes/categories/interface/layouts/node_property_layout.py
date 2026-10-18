import bpy

from .....sockets.spec import Boolean, Interface
from ....base_node import ScriptingBaseNode
from ._sublayout import sublayout


class SNA_Node_PropertyLayout(ScriptingBaseNode, bpy.types.Node):
    """How the properties after it are laid out (label split, decorators).
    They're drawn in a layout of their own, so elements before it and after
    a Reset Layout keep their layout."""

    bl_idname = "SNA_Node_PropertyLayout"
    bl_label = "Set Property Layout"
    sn_inputs = [
        Interface(),
        Boolean("decorate", "Decorated", default=False),
        Boolean("split", "Split", default=False),
    ]
    sn_outputs = [Interface("next")]

    def emit(self, ctx):
        layout, create = sublayout(ctx)
        ctx.code(f"""
            {create}
            {layout}.use_property_decorate = {ctx.input("decorate")}
            {layout}.use_property_split = {ctx.input("split")}
            {ctx.flow("next", layout=layout, horizontal=ctx.horizontal)}
        """)
