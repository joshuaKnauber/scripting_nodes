import bpy

from .....sockets.spec import Vector
from ....base_node import ScriptingBaseNode


class SNA_Node_Vector(ScriptingBaseNode, bpy.types.Node):
    """A constant vector with 2 to 4 components."""

    bl_idname = "SNA_Node_Vector"
    bl_label = "Vector"
    sn_header_props = ("dimension",)

    dimension: bpy.props.EnumProperty(
        name="Dimensions",
        description="Vector dimensions",
        items=[
            ("2", "Vec2", "Two-dimensional vector"),
            ("3", "Vec3", "Three-dimensional vector"),
            ("4", "Vec4", "Four-dimensional vector (with w component)"),
        ],
        default="3",
    )
    vector: bpy.props.FloatVectorProperty(
        name="Vector",
        size=4,
        default=(0.0, 0.0, 0.0, 0.0),
    )

    def socket_specs(self):
        return [], [Vector("vector", "Vector", dimension=int(self.dimension))]

    def draw(self, context, layout):
        col = layout.column(align=True)
        for i in range(int(self.dimension)):
            col.prop(self, "vector", index=i, text="")

    def emit(self, ctx):
        values = self.vector[: int(self.dimension)]
        ctx.output("vector", f"({', '.join(repr(float(v)) for v in values)})")
