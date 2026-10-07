import bpy

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

    def variable_name(self):
        return f"var_{self.id.lower()}"

    def emit(self, ctx):
        name = self.variable_name()
        ctx.output("variable", name)
        ctx.code(f"""
            {name} = {ctx.input("value")}
            {ctx.flow("next")}
        """)
