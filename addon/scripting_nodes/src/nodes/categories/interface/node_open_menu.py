import bpy

from ....core.context import NodeError
from ....core.references import Reference
from ....sockets.spec import Flow
from ..._reference_types import OPENABLE_NODES, open_call
from ...base_node import ScriptingBaseNode


class SNA_Node_OpenMenu(ScriptingBaseNode, bpy.types.Node):
    """Open a menu, pie menu or panel of this add-on at the mouse, e.g. from
    an operator."""

    bl_idname = "SNA_Node_OpenMenu"
    bl_label = "Open Menu"
    sn_inputs = [Flow()]
    sn_outputs = [Flow("next")]

    menu: Reference(
        OPENABLE_NODES, name="Menu", description="A Menu, Pie Menu or Panel node"
    )

    def draw(self, context, layout):
        self.draw_reference(layout, "menu")

    def emit(self, ctx):
        target = ctx.resolve("menu")
        if target is None:
            raise NodeError("Pick a menu")
        operator, properties = open_call(target)
        args = ", ".join(f"{name}={value}" for name, value in properties.items())
        ctx.code(f"""
            bpy.ops.{operator}({args})
            {ctx.flow("next")}
        """)
