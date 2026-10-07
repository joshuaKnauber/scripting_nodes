import bpy

from .....sockets.spec import String
from ....base_node import ScriptingBaseNode


class SNA_Node_String(ScriptingBaseNode, bpy.types.Node):
    """A constant text."""

    bl_idname = "SNA_Node_String"
    bl_label = "String"
    sn_outputs = [String("value", "String")]

    value: bpy.props.StringProperty(default="", options={"TEXTEDIT_UPDATE"})

    def draw(self, context, layout):
        layout.prop(self, "value", text="", placeholder="Value")

    def emit(self, ctx):
        ctx.output("value", repr(self.value))
