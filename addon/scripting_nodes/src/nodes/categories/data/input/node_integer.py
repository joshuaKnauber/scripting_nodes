import bpy

from .....sockets.spec import Integer
from ....base_node import ScriptingBaseNode


class SNA_Node_Integer(ScriptingBaseNode, bpy.types.Node):
    """A constant whole number."""

    bl_idname = "SNA_Node_Integer"
    bl_label = "Integer"
    sn_outputs = [Integer("value", "Integer")]

    value: bpy.props.IntProperty(default=1)

    def draw(self, context, layout):
        layout.prop(self, "value", text="")

    def emit(self, ctx):
        ctx.output("value", repr(int(self.value)))
