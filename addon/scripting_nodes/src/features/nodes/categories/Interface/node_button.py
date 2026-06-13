"""Button node - draws a layout.operator() button in the UI.

Targets either an SN Operator node or a built-in Blender operator. Operator
properties become input sockets and are emitted as `op.prop = value`
assignments after the `layout.operator(...)` call.
"""
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
from ..._operator_call import OperatorCallMixin
import bpy


class SNA_Node_Button(OperatorCallMixin, ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Button"
    bl_label = "Button"

    # Fixed inputs: [0] Interface chain, [1] Label. Op-args follow.
    operator_arg_offset = 2

    emboss: bpy.props.BoolProperty(
        name="Emboss",
        description="Draw the button with an embossed look",
        default=True,
        update=OperatorCallMixin.update_operator_target,
    )

    depress: bpy.props.BoolProperty(
        name="Depress",
        description="Draw the button as if it were pressed",
        default=False,
        update=OperatorCallMixin.update_operator_target,
    )

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        self.add_input("ScriptingStringSocket", "Label").value = "Run"
        self.add_output("ScriptingInterfaceSocket")

    def draw(self, context, layout):
        self.draw_operator_picker(layout)
        layout.prop(self, "emboss")
        layout.prop(self, "depress")

    def generate(self):
        bl_idname = self._resolved_bl_idname()
        # No operator chosen - just pass the interface flow through.
        if not bl_idname:
            self.code_inline = f"""
                {indent(self.outputs[0].eval(), 4)}
            """
            return

        op_var = f"op_{self.id}"
        layout_var = self.inputs[0].get_layout()
        label_code = self.inputs["Label"].eval()

        call = (
            f'{op_var} = {layout_var}.operator("{bl_idname}", '
            f"text={label_code}, "
            f"emboss={self.emboss}, depress={self.depress})"
        )
        prop_lines = self.emit_op_property_lines(op_var)

        body = call
        if prop_lines:
            body = f"{call}\n{prop_lines}"

        self.code_inline = f"""
            {indent(body, 3)}
            {indent(self.outputs[0].eval(), 3)}
        """
