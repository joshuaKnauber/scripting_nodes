import bpy

from ....sockets.spec import Icon, Integer, Interface
from ..._icon import icon_argument
from ..._text_source import TextSourceMixin
from ...base_node import ScriptingBaseNode


class SNA_Node_MultilineLabel(TextSourceMixin, ScriptingBaseNode, bpy.types.Node):
    """Text over several lines, wrapped to the width of the layout
    (layout.label_multiline where Blender has it, else one label per line)."""

    bl_idname = "SNA_Node_MultilineLabel"
    bl_label = "Multiline Label"
    bl_width_default = 200

    alignment: bpy.props.EnumProperty(
        name="Alignment",
        items=[
            ("LEFT", "Left", "", "ALIGN_LEFT", 0),
            ("CENTER", "Center", "", "ALIGN_CENTER", 1),
            ("RIGHT", "Right", "", "ALIGN_RIGHT", 2),
        ],
    )

    def socket_specs(self):
        inputs = [
            Interface(),
            self.text_input_spec(),
            Icon(),
            Integer("max_lines", "Max Lines", default=0),
        ]
        return inputs, [Interface("next")]

    def draw(self, context, layout):
        self.draw_text_block(layout)
        layout.prop(self, "alignment", expand=True)

    def emit(self, ctx):
        args = [ctx.layout, self.text_expression(ctx)]
        max_lines = ctx.input("max_lines")
        if max_lines != "0":
            args.append(f"max_lines={max_lines}")
        if self.alignment != "LEFT":
            args.append(f"alignment={self.alignment!r}")
        icon = icon_argument(ctx)
        if icon:
            args.append(icon)
        ctx.code(f"""
            {ctx.helper("label_multiline")}({", ".join(args)})
            {ctx.flow("next")}
        """)
