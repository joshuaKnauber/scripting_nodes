import bpy

from ....sockets.spec import Interface
from ..._text_source import TextSourceMixin
from ...base_node import ScriptingBaseNode


class SNA_Node_Markdown(TextSourceMixin, ScriptingBaseNode, bpy.types.Node):
    """Text formatted with markdown: headers, lists, bold / italic / code,
    links, quotes and rules (layout.label_markdown where Blender has it,
    else plain labels)."""

    bl_idname = "SNA_Node_Markdown"
    bl_label = "Markdown"
    bl_width_default = 200

    def socket_specs(self):
        return [Interface(), self.text_input_spec()], [Interface("next")]

    def draw(self, context, layout):
        self.draw_text_block(layout)

    def emit(self, ctx):
        text = self.text_expression(ctx)
        ctx.code(f"""
            {ctx.helper("sn_label_markdown")}({ctx.layout}, {text})
            {ctx.flow("next")}
        """)
