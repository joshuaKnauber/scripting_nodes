import bpy

from ....sockets.spec import Icon, Interface, String
from ..._icon import icon_argument
from ...base_node import ScriptingBaseNode


class SNA_Node_Link(ScriptingBaseNode, bpy.types.Node):
    """A link that opens a web page (layout.link, Blender 5.2; a button
    before)."""

    bl_idname = "SNA_Node_Link"
    bl_label = "Link"
    sn_inputs = [
        Interface(),
        String("url", "URL", default="https://www.blender.org"),
        String("text", "Text"),
        Icon(),
    ]
    sn_outputs = [Interface("next")]

    def emit(self, ctx):
        args = [ctx.layout, ctx.input("url")]
        text = self.socket("text")
        if text.is_linked or text.value:
            args.append(f"text={ctx.input('text')}")
        icon = icon_argument(ctx)
        if icon:
            args.append(icon)
        ctx.code(f"""
            {ctx.helper("sn_link")}({", ".join(args)})
            {ctx.flow("next")}
        """)
