import bpy

from ....sockets.spec import Socket
from ....core import properties
from ..._property_target import PropertyTargetMixin
from ...base_node import ScriptingBaseNode


def value_spec(node, key, label):
    """Socket for the values of the property `node` targets."""
    spec = Socket(node.target_data_type(), key, label)
    prop = node.target_prop()
    if prop is not None:
        spec.attrs.update(properties.socket_attrs(prop))
    return spec


class SNA_Node_GetProperty(PropertyTargetMixin, ScriptingBaseNode, bpy.types.Node):
    """The value of a property of this addon or of Blender."""

    bl_idname = "SNA_Node_GetProperty"
    bl_label = "Get Property"

    def socket_specs(self):
        return [self.data_input_spec()], [value_spec(self, "value", "Value")]

    def draw(self, context, layout):
        self.draw_target(layout)

    def emit(self, ctx):
        data, name = self.property_target(ctx)
        ctx.output("value", f"{data}.{name}")
