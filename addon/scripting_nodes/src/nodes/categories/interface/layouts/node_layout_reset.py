import bpy

from .....sockets.spec import Interface
from ....base_node import ScriptingBaseNode


def root_layout(scope):
    """The outermost layout of the flow (the panel's/menu's own layout)."""
    layout = None
    while scope is not None:
        if scope.layout:
            layout = scope.layout
        scope = scope.parent
    return layout or "self.layout"


class SNA_Node_LayoutReset(ScriptingBaseNode, bpy.types.Node):
    """Continue drawing in the panel's own layout, outside of rows, boxes, ..."""

    bl_idname = "SNA_Node_LayoutReset"
    bl_label = "Reset Layout"
    sn_inputs = [Interface()]
    sn_outputs = [Interface("next", "Continue"), Interface("reset", "Layout")]

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.flow("next")}
            {ctx.flow("reset", layout=root_layout(ctx.scope))}
        """)
