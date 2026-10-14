import bpy

from ....core.context import NodeError
from ....core.references import Reference
from ....sockets.spec import Flow, Socket
from ..._reference_types import VARIABLE_NODES, usable_variable
from ...base_node import ScriptingBaseNode


class SNA_Node_SetVariable(ScriptingBaseNode, bpy.types.Node):
    """Change the value of a variable."""

    bl_idname = "SNA_Node_SetVariable"
    bl_label = "Set Variable"

    var: Reference(VARIABLE_NODES, name="Variable", filter=usable_variable)
    operation: bpy.props.EnumProperty(
        name="Operation",
        items=[
            ("SET", "Set", "Give the variable a new value"),
            ("ADD", "Change By", "Add to the value (numbers, text, lists)"),
            ("TOGGLE", "Toggle", "Switch a boolean between True and False"),
        ],
    )

    def socket_specs(self):
        target = self.resolve_reference("var")
        data_type = target.data_type if target else "ScriptingDataSocket"
        label = "Amount" if self.operation == "ADD" else "Value"
        value = Socket(data_type, "value", label, enabled=self.operation != "TOGGLE")
        return [Flow(), value], [Flow("next")]

    def draw(self, context, layout):
        self.draw_reference(layout, "var")
        layout.prop(self, "operation", text="")

    def emit(self, ctx):
        target = ctx.resolve("var")
        if target is None:
            raise NodeError("Pick a variable")
        if not usable_variable(self, target):
            raise NodeError("Local variables can only be used in their own tree")
        local = target.bl_idname == "SNA_Node_LocalVariable"
        if local:
            current = target.variable_name()
        else:
            current = f"{ctx.symbol(target, target.getter_name())}()"
        if self.operation == "TOGGLE":
            value = f"not {current}"
        elif self.operation == "ADD":
            value = f"{current} + {ctx.input('value')}"
        else:
            value = ctx.input("value")
        if local:
            statement = f"{target.variable_name()} = {value}"
        else:
            statement = f"{ctx.symbol(target, target.setter_name())}({value})"
        ctx.code(f"""
            {statement}
            {ctx.flow("next")}
        """)
