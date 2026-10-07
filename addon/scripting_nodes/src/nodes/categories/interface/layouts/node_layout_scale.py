import bpy

from .....sockets.spec import Float, Interface
from ....base_node import ScriptingBaseNode


class SNA_Node_LayoutScale(ScriptingBaseNode, bpy.types.Node):
    """Scale the following elements of the layout, or give them a fixed size.
    0 keeps Blender's default."""

    bl_idname = "SNA_Node_LayoutScale"
    bl_label = "Set Layout Scale"

    fixed_scale: bpy.props.BoolProperty(
        name="Fixed Scale",
        description="Set a fixed size in UI units instead of a scale factor",
    )

    def socket_specs(self):
        prefix = "Units" if self.fixed_scale else "Scale"
        inputs = [
            Interface(),
            Float("x", f"{prefix} X", default=0.0),
            Float("y", f"{prefix} Y", default=0.0),
        ]
        return inputs, [Interface("next")]

    def draw(self, context, layout):
        layout.prop(self, "fixed_scale")

    def emit(self, ctx):
        attr = "ui_units" if self.fixed_scale else "scale"
        ctx.code(f"""
            {ctx.layout}.{attr}_x = {ctx.input("x")}
            {ctx.layout}.{attr}_y = {ctx.input("y")}
            {ctx.flow("next")}
        """)
