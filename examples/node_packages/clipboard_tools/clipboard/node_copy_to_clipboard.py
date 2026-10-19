import bpy

from . import sn


class CT_Node_CopyToClipboard(sn.ScriptingBaseNode, bpy.types.Node):
    """Put text on the system clipboard."""

    bl_idname = "CT_Node_CopyToClipboard"
    bl_label = "Copy to Clipboard"
    sn_inputs = [sn.Flow(), sn.String("text", "Text")]
    sn_outputs = [sn.Flow("next")]

    def emit(self, ctx):
        ctx.code(f"""
            bpy.context.window_manager.clipboard = {ctx.input("text")}
            {ctx.flow("next")}
        """)
