import bpy

from ....sockets.spec import Flow
from ..._property_target import PropertyTargetMixin
from ...base_node import ScriptingBaseNode
from .node_get_property import value_spec


class SNA_Node_SetProperty(PropertyTargetMixin, ScriptingBaseNode, bpy.types.Node):
    """Change a property of this addon or of Blender."""

    bl_idname = "SNA_Node_SetProperty"
    bl_label = "Set Property"

    def socket_specs(self):
        inputs = [Flow(), self.data_input_spec(), value_spec(self, "value", "Value")]
        return inputs, [Flow("next")]

    def draw(self, context, layout):
        self.draw_target(layout)

    def emit(self, ctx):
        data, name = self.property_target(ctx)
        ctx.code(f"""
            {data}.{name} = {ctx.input("value")}
            {ctx.flow("next")}
        """)
