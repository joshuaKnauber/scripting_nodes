import bpy

from ....sockets.socket_types import DATA_SOCKET_ENUM_ITEMS
from ....sockets.spec import Boolean, Socket
from ...base_node import ScriptingBaseNode


class SNA_Node_SwitchData(ScriptingBaseNode, bpy.types.Node):
    """Pick one of two values depending on a condition."""

    bl_idname = "SNA_Node_SwitchData"
    bl_label = "Switch Data"
    sn_header_props = ("data_type",)

    data_type: bpy.props.EnumProperty(
        items=DATA_SOCKET_ENUM_ITEMS, name="Output Data Type"
    )

    def socket_specs(self):
        inputs = [
            Boolean("condition", "Condition"),
            Socket(self.data_type, "false", "False"),
            Socket(self.data_type, "true", "True"),
        ]
        return inputs, [Socket(self.data_type, "result", "Result")]

    def emit(self, ctx):
        condition = ctx.input("condition")
        true_value, false_value = ctx.input("true"), ctx.input("false")
        ctx.output("result", f"{true_value} if {condition} else {false_value}")
