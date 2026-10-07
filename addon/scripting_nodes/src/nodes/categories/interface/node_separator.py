import bpy

from ....sockets.spec import Float, Interface
from ...base_node import ScriptingBaseNode


class SNA_Node_Separator(ScriptingBaseNode, bpy.types.Node):
    """Space or a line between UI elements."""

    bl_idname = "SNA_Node_Separator"
    bl_label = "Separator"
    sn_inputs = [Interface(), Float("factor", "Factor", default=1.0)]
    sn_outputs = [Interface("next")]

    line: bpy.props.BoolProperty(name="Show Line", description="Draw a line")

    def draw(self, context, layout):
        layout.prop(self, "line")

    def emit(self, ctx):
        kind = "LINE" if self.line else "SPACE"
        ctx.code(f"""
            {ctx.layout}.separator(factor={ctx.input("factor")}, type={kind!r})
            {ctx.flow("next")}
        """)
