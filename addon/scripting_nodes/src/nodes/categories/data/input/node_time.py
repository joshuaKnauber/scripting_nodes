import bpy

from .....sockets.spec import Float, String
from ....base_node import ScriptingBaseNode


class SNA_Node_CurrentTime(ScriptingBaseNode, bpy.types.Node):
    """The current date and time as text (Format: %Y year, %m month, %d day,
    %H hour, %M minute, %S second) and as seconds since 1970."""

    bl_idname = "SNA_Node_CurrentTime"
    bl_label = "Current Time"
    sn_inputs = [String("format", "Format", default="%Y-%m-%d %H:%M:%S")]
    sn_outputs = [String("text", "Text"), Float("seconds", "Seconds")]

    def emit(self, ctx):
        ctx.imports("import time")
        ctx.output("text", f"time.strftime({ctx.input('format')})")
        ctx.output("seconds", "time.time()")
