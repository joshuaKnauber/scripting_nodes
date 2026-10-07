import bpy

from .....sockets.spec import Boolean
from ....base_node import ScriptingBaseNode


class SNA_Node_Boolean(ScriptingBaseNode, bpy.types.Node):
    """A constant True or False."""

    bl_idname = "SNA_Node_Boolean"
    bl_label = "Boolean"
    sn_outputs = [Boolean("value", "Boolean")]

    value: bpy.props.BoolProperty(default=True)

    def draw(self, context, layout):
        layout.prop(self, "value", text="Value")

    def emit(self, ctx):
        ctx.output("value", repr(bool(self.value)))
