import bpy

from ....sockets.spec import Float, Vector
from ...base_node import ScriptingBaseNode

AXES = "xyzw"
DIMENSIONS = [("2", "2D", ""), ("3", "3D", ""), ("4", "4D", "")]


class SNA_Node_CombineVector(ScriptingBaseNode, bpy.types.Node):
    """A vector from its X, Y, Z (and W) values."""

    bl_idname = "SNA_Node_CombineVector"
    bl_label = "Combine Vector"
    sn_header_props = ("dimension",)

    dimension: bpy.props.EnumProperty(name="Dimensions", items=DIMENSIONS, default="3")

    def socket_specs(self):
        size = int(self.dimension)
        inputs = [Float(axis, axis.upper()) for axis in AXES[:size]]
        return inputs, [Vector("vector", "Vector", dimension=size)]

    def emit(self, ctx):
        values = ", ".join(ctx.input(axis) for axis in AXES[: int(self.dimension)])
        ctx.output("vector", f"({values})")


class SNA_Node_SeparateVector(ScriptingBaseNode, bpy.types.Node):
    """The X, Y, Z (and W) values of a vector."""

    bl_idname = "SNA_Node_SeparateVector"
    bl_label = "Separate Vector"
    sn_header_props = ("dimension",)

    dimension: bpy.props.EnumProperty(name="Dimensions", items=DIMENSIONS, default="3")

    def socket_specs(self):
        size = int(self.dimension)
        outputs = [Float(axis, axis.upper()) for axis in AXES[:size]]
        return [Vector("vector", "Vector", dimension=size)], outputs

    def emit(self, ctx):
        vector = ctx.input("vector")
        for i, axis in enumerate(AXES[: int(self.dimension)]):
            ctx.output(axis, f"{vector}[{i}]")
