"""Run Operator node - invokes an operator from a program flow.

Targets either an SN Operator node (referenced via the signature picker) or
a built-in Blender operator (chosen from a searchable enum). Operator
properties become input sockets that get reconciled when the chosen
operator changes; their values are emitted as kwargs to the bpy.ops call.
"""
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
from ..._operator_call import (
    EXEC_CONTEXT_ITEMS,
    OperatorCallMixin,
)
import bpy


class SNA_Node_RunOperator(
    OperatorCallMixin, ScriptingBaseNode, bpy.types.Node
):
    bl_idname = "SNA_Node_RunOperator"
    bl_label = "Run Operator"

    # Only the Before socket precedes the dynamic op-arg sockets.
    operator_arg_offset = 1

    exec_context: bpy.props.EnumProperty(
        name="Context",
        description="Execution context passed to the operator call",
        items=EXEC_CONTEXT_ITEMS,
        default="EXEC_DEFAULT",
        update=OperatorCallMixin.update_operator_target,
    )

    def on_create(self):
        self.add_input("ScriptingLogicSocket")
        self.add_output("ScriptingLogicSocket")

    def draw(self, context, layout):
        self.draw_operator_picker(layout)
        layout.prop(self, "exec_context", text="")

    def generate(self):
        bl_idname = self._resolved_bl_idname()
        # If no operator chosen, just pass through the program flow.
        if not bl_idname:
            self.code_inline = f"""
                {indent(self.outputs[0].eval(), 4)}
            """
            return

        kwargs = self.emit_kwargs_inline()
        # Build the args string: context first, then kwargs.
        args = f"'{self.exec_context}'"
        if kwargs:
            args = f"{args}, {kwargs}"

        self.code_inline = f"""
            bpy.ops.{bl_idname}({args})
            {indent(self.outputs[0].eval(), 4)}
        """
