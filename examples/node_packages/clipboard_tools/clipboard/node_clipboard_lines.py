import bpy

from . import sn


class CT_Node_ClipboardLines(sn.ScriptingBaseNode, bpy.types.Node):
    """The lines of the text on the clipboard, as a list."""

    bl_idname = "CT_Node_ClipboardLines"
    bl_label = "Clipboard Lines"
    sn_outputs = [sn.List("lines", "Lines")]

    skip_empty: bpy.props.BoolProperty(
        name="Skip Empty", description="Leave out empty lines", default=True
    )

    def draw(self, context, layout):
        layout.prop(self, "skip_empty")

    def emit(self, ctx):
        lines = "bpy.context.window_manager.clipboard.splitlines()"
        if self.skip_empty:
            line = ctx.var("line")
            lines = f"[{line} for {line} in {lines} if {line}.strip()]"
        ctx.output("lines", lines)
