import bpy

from ....core.context import NodeError
from ....core.references import Reference
from ....sockets.spec import Socket
from ..._reference_types import VARIABLE_NODES, usable_variable
from ...base_node import ScriptingBaseNode


class SNA_Node_GetVariable(ScriptingBaseNode, bpy.types.Node):
    """The current value of a variable."""

    bl_idname = "SNA_Node_GetVariable"
    bl_label = "Get Variable"

    var: Reference(VARIABLE_NODES, name="Variable", filter=usable_variable)

    def socket_specs(self):
        target = self.resolve_reference("var")
        data_type = target.data_type if target else "ScriptingDataSocket"
        return [], [Socket(data_type, "value", "Value")]

    def draw(self, context, layout):
        self.draw_reference(layout, "var")

    def emit(self, ctx):
        target = ctx.resolve("var")
        if target is None:
            raise NodeError("Pick a variable")
        if not usable_variable(self, target):
            raise NodeError("Local variables can only be used in their own tree")
        if target.bl_idname == "SNA_Node_LocalVariable":
            ctx.output("value", target.variable_name())
        else:
            ctx.output("value", f"{ctx.symbol(target, target.getter_name())}()")
