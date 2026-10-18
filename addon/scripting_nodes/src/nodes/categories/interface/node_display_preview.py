import bpy

from ....core import naming
from ....core.context import NodeError
from ....sockets.spec import BlendData, Boolean, Interface
from ...base_node import ScriptingBaseNode


class SNA_Node_DisplayPreview(ScriptingBaseNode, bpy.types.Node):
    """Draws the rendered preview of a material, texture, light or world,
    like the one in the Material Properties."""

    bl_idname = "SNA_Node_DisplayPreview"
    bl_label = "Display Preview"
    sn_inputs = [
        Interface(),
        BlendData("data", "Data", "ID"),
        Boolean("show_buttons", "Show Buttons", default=True),
    ]
    sn_outputs = [Interface("next")]

    def sn_names(self):
        # each preview remembers its own size
        return [naming.Idname("preview_id", naming.label(self, socket=None))]

    def emit(self, ctx):
        if not ctx.is_linked("data"):
            raise NodeError("Connect a material, texture, light or world")
        data = ctx.var("preview_data")
        args = ctx.args(
            data,
            ctx.keyword("show_buttons", "show_buttons", True),
            f"preview_id={ctx.name('preview_id')!r}",
        )
        # no preview for None: Blender needs a data-block
        ctx.code(f"""
            {data} = {ctx.input("data")}
            if {data} is not None:
                {ctx.layout}.template_preview({args})
            {ctx.flow("next")}
        """)
