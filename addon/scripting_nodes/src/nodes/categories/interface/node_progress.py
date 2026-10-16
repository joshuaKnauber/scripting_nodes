import bpy

from ....sockets.spec import Float, Interface, String
from ...base_node import ScriptingBaseNode


class SNA_Node_Progress(ScriptingBaseNode, bpy.types.Node):
    """A progress bar or ring, Factor from 0 to 1."""

    bl_idname = "SNA_Node_Progress"
    bl_label = "Progress"
    sn_inputs = [
        Interface(),
        Float("factor", "Factor", default=0.5),
        String("text", "Text"),
    ]
    sn_outputs = [Interface("next")]
    sn_header_props = ("progress_type",)

    progress_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("BAR", "Bar", "A bar with the text in it"),
            ("RING", "Ring", "A ring next to the text"),
        ],
    )

    def emit(self, ctx):
        args = [ctx.keyword("factor", "factor", 0.0), ctx.keyword("text", "text", "")]
        args = [arg for arg in args if arg]
        if self.progress_type != "BAR":
            args.append(f"type={self.progress_type!r}")
        ctx.code(f"""
            {ctx.layout}.progress({", ".join(args)})
            {ctx.flow("next")}
        """)
