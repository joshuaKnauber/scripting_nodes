import bpy

from ....core.context import NodeError
from ....sockets.spec import Socket
from ..._reference_signatures import VARIABLE_NODES
from ...base_node import ScriptingBaseNode


class SNA_Node_GetVariable(ScriptingBaseNode, bpy.types.Node):
    """The current value of a variable."""

    bl_idname = "SNA_Node_GetVariable"
    bl_label = "Get Variable"
    sn_reference_properties = {"var": VARIABLE_NODES}

    var: bpy.props.StringProperty(name="Variable")

    def socket_specs(self):
        target = self.resolve_reference("var")
        data_type = target.data_type if target else "ScriptingDataSocket"
        return [], [Socket(data_type, "value", "Value")]

    def draw(self, context, layout):
        self.draw_reference_prop(layout, "var")

    def emit(self, ctx):
        target = ctx.resolve("var")
        if target is None:
            raise NodeError("Pick a variable")
        if target.bl_idname == "SNA_Node_LocalVariable":
            ctx.output("value", target.variable_name())
        else:
            ctx.output("value", f"{ctx.symbol(target, target.getter_name())}()")
