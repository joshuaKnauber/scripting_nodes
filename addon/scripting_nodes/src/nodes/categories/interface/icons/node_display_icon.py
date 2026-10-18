import bpy

from .....core.context import NodeError
from .....sockets.spec import Float, Icon, Interface
from ...._icon import builtin_icon
from ....base_node import ScriptingBaseNode


class SNA_Node_DisplayIcon(ScriptingBaseNode, bpy.types.Node):
    """Draws an icon on its own, at any size: a logo, a big preview. Only
    custom icons and previews get bigger; Blender draws its own icons at
    their normal size in the larger space."""

    bl_idname = "SNA_Node_DisplayIcon"
    bl_label = "Display Icon"
    sn_inputs = [
        Interface(),
        Icon(default="BLENDER"),
        Float("scale", "Scale", default=1.0),
    ]
    sn_outputs = [Interface("next")]

    def emit(self, ctx):
        socket = self.socket("icon")
        if not socket.is_linked:
            if not socket.value:
                raise NodeError("Pick an icon")
            builtin_icon(socket.value)  # known to this Blender
        # template_icon takes an icon id, the socket gives one
        args = ctx.args(
            f"icon_value={ctx.input('icon')}", ctx.keyword("scale", "scale", 1.0)
        )
        ctx.code(f"""
            {ctx.layout}.template_icon({args})
            {ctx.flow("next")}
        """)
