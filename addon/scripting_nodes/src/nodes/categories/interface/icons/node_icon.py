import bpy

from .....lib.icons import draw_icon_picker
from .....sockets.spec import Icon
from ...._icon import builtin_icon
from ....base_node import ScriptingBaseNode


class SNA_Node_Icon(ScriptingBaseNode, bpy.types.Node):
    """One of Blender's icons."""

    bl_idname = "SNA_Node_Icon"
    bl_label = "Icon"
    bl_width_default = 200
    sn_outputs = [Icon("icon", "Icon")]

    icon: bpy.props.StringProperty(name="Icon", default="BLENDER")

    def draw(self, context, layout):
        draw_icon_picker(layout, self, "icon", show_name=True)

    def emit(self, ctx):
        if not self.icon:
            ctx.output("icon", "0")
            return
        builtin_icon(self.icon)  # known to this Blender
        ctx.output("icon", f"{ctx.helper('sn_icon')}({self.icon!r})")
