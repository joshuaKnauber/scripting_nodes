import bpy

from ....core.context import NodeError
from ....core.references import Reference
from ....sockets.spec import Icon, Interface, String
from ..._icon import icon_argument
from ...base_node import ScriptingBaseNode


class SNA_Node_Popover(ScriptingBaseNode, bpy.types.Node):
    """A button opening a panel as a popup. The panel still shows where it's
    placed; put it in a Header region to only have it as a popover."""

    bl_idname = "SNA_Node_Popover"
    bl_label = "Popover"
    sn_inputs = [Interface(), String("label", "Label"), Icon()]
    sn_outputs = [Interface("next")]

    panel: Reference(("SNA_Node_Panel",), name="Panel", description="A Panel node")

    def draw(self, context, layout):
        self.draw_reference(layout, "panel")

    def emit(self, ctx):
        target = ctx.resolve("panel")
        if target is None:
            raise NodeError("Pick a panel")
        args = [repr(target.sn_name("class")), f"text={ctx.input('label')}"]
        icon = icon_argument(ctx)
        if icon:
            args.append(icon)
        ctx.code(f"""
            {ctx.layout}.popover({", ".join(args)})
            {ctx.flow("next")}
        """)
