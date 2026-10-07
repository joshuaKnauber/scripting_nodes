"""Button node - draws a layout.operator() button in the UI.

Targets either an SN Operator node or a built-in Blender operator. Operator
properties become input sockets and are set on the returned operator
properties (`op.prop = value`) after the `layout.operator(...)` call.
"""

import bpy

from ....core.context import NodeError
from ....sockets.spec import Interface, String
from ..._operator_call import OperatorCallMixin
from ...base_node import ScriptingBaseNode


class SNA_Node_Button(OperatorCallMixin, ScriptingBaseNode, bpy.types.Node):
    """A button that runs an operator."""

    bl_idname = "SNA_Node_Button"
    bl_label = "Button"
    fixed_inputs = [Interface(), String("label", "Label", default="Run")]
    fixed_outputs = [Interface("next")]

    emboss: bpy.props.BoolProperty(
        name="Emboss", description="Draw the button with an embossed look", default=True
    )
    depress: bpy.props.BoolProperty(
        name="Depress", description="Draw the button as if it were pressed"
    )

    def draw(self, context, layout):
        self.draw_operator_picker(layout)
        row = layout.row(align=True)
        row.prop(self, "emboss", toggle=True)
        row.prop(self, "depress", toggle=True)

    def emit(self, ctx):
        idname = self.operator_idname()
        if not idname:
            raise NodeError("Pick an operator")
        args = [repr(idname), f"text={ctx.input('label')}"]
        if not self.emboss:
            args.append("emboss=False")
        if self.depress:
            args.append("depress=True")
        call = f"{ctx.layout}.operator({', '.join(args)})"

        props = self.operator_args(ctx)
        if not props:
            ctx.code(f"""
                {call}
                {ctx.flow("next")}
            """)
            return
        op = ctx.var("op")
        ctx.code(f"""
            {op} = {call}
            {ctx.join(f"{op}.{name} = {value}" for name, value in props)}
            {ctx.flow("next")}
        """)
