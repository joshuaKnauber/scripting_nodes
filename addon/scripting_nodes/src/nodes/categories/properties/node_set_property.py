import bpy

from ....sockets.spec import Flow
from ..._property_target import PropertyTargetMixin
from ...base_node import ScriptingBaseNode


class SNA_Node_SetProperty(PropertyTargetMixin, ScriptingBaseNode, bpy.types.Node):
    """Change a property of this addon or of Blender."""

    bl_idname = "SNA_Node_SetProperty"
    bl_label = "Set Property"
    bl_width_default = 200

    def socket_specs(self):
        inputs = [Flow(), self.target_value_spec("value", "Value")]
        inputs += self.target_input_specs()  # owner and path keys last
        return inputs, [Flow("next")]

    def draw(self, context, layout):
        self.draw_target(layout)

    def emit(self, ctx):
        data, name = self.property_target(ctx)
        ctx.code(f"""
            {data}.{name} = {ctx.input("value")}
            {ctx.flow("next")}
        """)
