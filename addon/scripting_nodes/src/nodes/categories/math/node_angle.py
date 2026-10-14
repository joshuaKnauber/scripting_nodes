import bpy

from ....sockets.spec import Float
from ...base_node import ScriptingBaseNode


class SNA_Node_ConvertAngle(ScriptingBaseNode, bpy.types.Node):
    """Convert an angle between degrees and radians. Blender stores angles
    in radians and shows them in degrees."""

    bl_idname = "SNA_Node_ConvertAngle"
    bl_label = "Convert Angle"
    sn_inputs = [Float("angle", "Angle")]
    sn_outputs = [Float("angle", "Angle")]
    sn_header_props = ("conversion",)

    conversion: bpy.props.EnumProperty(
        name="Conversion",
        items=[
            ("radians", "Degrees to Radians", "180 becomes 3.14"),
            ("degrees", "Radians to Degrees", "3.14 becomes 180"),
        ],
    )

    def emit(self, ctx):
        ctx.imports("import math")
        ctx.output("angle", f"math.{self.conversion}({ctx.input('angle')})")
