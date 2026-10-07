import bpy

from .....sockets.spec import Color
from ....base_node import ScriptingBaseNode


class SNA_Node_Color(ScriptingBaseNode, bpy.types.Node):
    """A constant RGB or RGBA color."""

    bl_idname = "SNA_Node_Color"
    bl_label = "Color"

    use_alpha: bpy.props.BoolProperty(
        name="Use Alpha",
        description="Include alpha channel in color values",
        default=False,
    )
    rgb_value: bpy.props.FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
    )
    rgba_value: bpy.props.FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )

    def socket_specs(self):
        return [], [Color("color", "Color", alpha=self.use_alpha)]

    def draw(self, context, layout):
        layout.prop(self, "use_alpha", text="Use Alpha")
        layout.prop(self, "rgba_value" if self.use_alpha else "rgb_value", text="")

    def emit(self, ctx):
        values = self.rgba_value if self.use_alpha else self.rgb_value
        ctx.output("color", f"({', '.join(repr(float(v)) for v in values)})")
