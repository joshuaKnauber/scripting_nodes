import bpy

from ....sockets.spec import Socket
from ..._property_target import PropertyTargetMixin
from ..._reference_signatures import PROPERTY_NODES
from ...base_node import ScriptingBaseNode


def value_spec(node, key, label):
    """Socket for the values of the property `node` targets."""
    idname = node.target_data_type()
    spec = Socket(idname, key, label)
    size = getattr(node.target_node(), "prop_size", None)
    if size and idname == "ScriptingVectorSocket" and 2 <= size <= 4:
        spec.attrs["dimension"] = str(size)
    elif idname == "ScriptingColorSocket":
        spec.attrs["use_alpha"] = size == 4
    return spec


class SNA_Node_GetProperty(PropertyTargetMixin, ScriptingBaseNode, bpy.types.Node):
    """The value of a property of this addon or of Blender."""

    bl_idname = "SNA_Node_GetProperty"
    bl_label = "Get Property"
    sn_reference_properties = {"prop": PROPERTY_NODES}

    def socket_specs(self):
        return [self.data_input_spec()], [value_spec(self, "value", "Value")]

    def draw(self, context, layout):
        self.draw_target(layout)

    def emit(self, ctx):
        data, name = self.property_target(ctx)
        ctx.output("value", f"{data}.{name}")
