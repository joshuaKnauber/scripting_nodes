import bpy

from ....core.context import NodeError
from ....sockets.spec import Flow, Socket
from ..._reference_signatures import VARIABLE_NODES
from ...base_node import ScriptingBaseNode


class SNA_Node_SetVariable(ScriptingBaseNode, bpy.types.Node):
    """Change the value of a variable."""

    bl_idname = "SNA_Node_SetVariable"
    bl_label = "Set Variable"
    sn_reference_properties = {"var": VARIABLE_NODES}

    var: bpy.props.StringProperty(name="Variable")

    def socket_specs(self):
        target = self.resolve_reference("var")
        data_type = target.data_type if target else "ScriptingDataSocket"
        return [Flow(), Socket(data_type, "value", "Value")], [Flow("next")]

    def draw(self, context, layout):
        self.draw_reference_prop(layout, "var")

    def emit(self, ctx):
        target = ctx.resolve("var")
        if target is None:
            raise NodeError("Pick a variable")
        value = ctx.input("value")
        if target.bl_idname == "SNA_Node_LocalVariable":
            statement = f"{target.variable_name()} = {value}"
        else:
            statement = f"{ctx.symbol(target, target.setter_name())}({value})"
        ctx.code(f"""
            {statement}
            {ctx.flow("next")}
        """)
