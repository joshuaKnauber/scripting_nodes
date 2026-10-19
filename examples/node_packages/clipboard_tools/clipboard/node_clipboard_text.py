import bpy

from . import sn


class CT_Node_ClipboardText(sn.ScriptingBaseNode, bpy.types.Node):
    """The text on the system clipboard."""

    bl_idname = "CT_Node_ClipboardText"
    bl_label = "Clipboard Text"
    sn_outputs = [sn.String("text", "Text")]

    def emit(self, ctx):
        ctx.output("text", "bpy.context.window_manager.clipboard")
