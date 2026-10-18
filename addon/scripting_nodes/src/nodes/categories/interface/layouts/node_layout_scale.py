import bpy

from .....sockets.spec import Float, Interface
from ....base_node import ScriptingBaseNode
from ._sublayout import sublayout


class SNA_Node_LayoutScale(ScriptingBaseNode, bpy.types.Node):
    """Scale the elements after it, or give them a fixed size. 0 keeps
    Blender's default. They're drawn in a layout of their own, so elements
    before it and after a Reset Layout keep their size."""

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
        layout, create = sublayout(ctx)
        settings = [
            f"{layout}.{attr}_{axis} = {ctx.input(axis)}"
            for axis in ("x", "y")
            if not ctx.is_default(axis, 0.0)
        ]
        ctx.code(f"""
            {create}
            {ctx.join(settings)}
            {ctx.flow("next", layout=layout, horizontal=ctx.horizontal)}
        """)
