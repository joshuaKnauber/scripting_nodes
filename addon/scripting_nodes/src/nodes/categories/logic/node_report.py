import bpy

from ....sockets.spec import Flow, String
from ...base_node import ScriptingBaseNode

KINDS = [
    ("INFO", "Info", "A message in the status bar", "INFO", 0),
    ("WARNING", "Warning", "A warning in the status bar", "ERROR", 1),
    ("ERROR", "Error", "An error in the status bar (and a popup)", "CANCEL", 2),
]


class SNA_Node_Report(ScriptingBaseNode, bpy.types.Node):
    """Show a message in the status bar and the Info editor. Only operators
    report; elsewhere the message is printed."""

    bl_idname = "SNA_Node_Report"
    bl_label = "Report"
    sn_inputs = [Flow(), String("message", "Message")]
    sn_outputs = [Flow("next")]
    sn_header_props = ("kind",)

    kind: bpy.props.EnumProperty(name="Type", items=KINDS)

    def emit(self, ctx):
        owner = "self" if "self" in ctx.scope.names else "None"
        ctx.code(f"""
            {ctx.helper("report")}({owner}, {self.kind!r}, {ctx.input("message")})
            {ctx.flow("next")}
        """)
