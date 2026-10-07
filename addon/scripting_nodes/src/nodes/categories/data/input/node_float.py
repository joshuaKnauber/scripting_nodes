import bpy

from .....sockets.spec import Float
from ....base_node import ScriptingBaseNode


class SNA_Node_Float(ScriptingBaseNode, bpy.types.Node):
    """A constant decimal number."""

    bl_idname = "SNA_Node_Float"
    bl_label = "Float"
    sn_outputs = [Float("value", "Float")]

    value: bpy.props.FloatProperty(default=1)

    def draw(self, context, layout):
        layout.prop(self, "value", text="")

    def emit(self, ctx):
        ctx.output("value", repr(float(self.value)))
