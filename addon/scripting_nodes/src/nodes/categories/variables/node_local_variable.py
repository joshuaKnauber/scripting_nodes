import bpy

from ....core import naming
from ....sockets.socket_types import DATA_SOCKET_ENUM_ITEMS
from ....sockets.spec import Flow, Socket
from ...base_node import ScriptingBaseNode


class SNA_Node_LocalVariable(ScriptingBaseNode, bpy.types.Node):
    """A variable that exists in the rest of this flow."""

    bl_idname = "SNA_Node_LocalVariable"
    bl_label = "Local Variable"
    sn_header_props = ("data_type",)

    data_type: bpy.props.EnumProperty(items=DATA_SOCKET_ENUM_ITEMS, name="Data Type")

    def socket_specs(self):
        return (
            [Flow(), Socket(self.data_type, "value", "Initial Value")],
            [Flow("next"), Socket(self.data_type, "variable", "Value")],
        )

    def sn_names(self):
        label = naming.label(self, socket=None, fallback=self.name)
        return [naming.Symbol("variable", naming.snake(label, "var"))]

    def variable_name(self):
        return self.sn_name("variable")

    def emit(self, ctx):
        name = ctx.name("variable")
        ctx.output("variable", name)
        ctx.code(f"""
            {name} = {ctx.input("value")}
            {ctx.flow("next")}
        """)
