"""Run Operator node - calls an operator from a program flow.

Targets either an SN Operator node or a built-in Blender operator. Operator
properties become input sockets, passed as keyword arguments to the
`bpy.ops` call.
"""

import bpy

from ....core.context import NodeError
from ....sockets.spec import Flow
from ..._operator_call import EXEC_CONTEXT_ITEMS, OperatorCallMixin
from ...base_node import ScriptingBaseNode


class SNA_Node_RunOperator(OperatorCallMixin, ScriptingBaseNode, bpy.types.Node):
    """Run an operator of this addon or of Blender."""

    bl_idname = "SNA_Node_RunOperator"
    bl_label = "Run Operator"
    fixed_inputs = [Flow()]
    fixed_outputs = [Flow("next")]

    exec_context: bpy.props.EnumProperty(
        name="Context",
        description="Execution context passed to the operator call",
        items=EXEC_CONTEXT_ITEMS,
        default="EXEC_DEFAULT",
    )

    def draw(self, context, layout):
        self.draw_operator_picker(layout)
        layout.prop(self, "exec_context", text="")

    def emit(self, ctx):
        idname = self.operator_idname()
        if not idname:
            raise NodeError("Pick an operator")
        args = []
        if self.exec_context != "EXEC_DEFAULT":
            args.append(repr(self.exec_context))
        args += [f"{name}={value}" for name, value in self.operator_args(ctx)]
        ctx.code(f"""
            bpy.ops.{idname}({", ".join(args)})
            {ctx.flow("next")}
        """)
