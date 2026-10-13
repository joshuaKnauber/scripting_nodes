import bpy

from ..._property_target import PropertyTargetMixin
from ...base_node import ScriptingBaseNode


class SNA_Node_GetProperty(PropertyTargetMixin, ScriptingBaseNode, bpy.types.Node):
    """The value of a property of this addon or of Blender."""

    bl_idname = "SNA_Node_GetProperty"
    bl_label = "Get Property"
    bl_width_default = 200

    def socket_specs(self):
        return self.target_input_specs(), [self.target_value_spec("value", "Value")]

    def draw(self, context, layout):
        self.draw_target(layout)

    def emit(self, ctx):
        data, name = self.property_target(ctx)
        ctx.output("value", f"{data}.{name}")
