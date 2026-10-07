import bpy

from ....sockets.spec import Flow
from ...base_node import ScriptingBaseNode
from ._base import GroupInterfaceMixin, _poll_group_tree


class SNA_Node_GroupOutput(GroupInterfaceMixin, ScriptingBaseNode, bpy.types.Node):
    """End of a group (function): its return values."""

    bl_idname = "SNA_Node_GroupOutput"
    bl_label = "Group Output"
    default_fallback = "result"

    @classmethod
    def poll(cls, ntree):
        return _poll_group_tree(cls, ntree)

    def socket_specs(self):
        return [Flow("function", "Function")] + self.item_specs(), []

    def emit(self, ctx):
        values = [ctx.input(key, default="None") for key in self.parameter_keys()]
        if not values:
            return
        result = values[0] if len(values) == 1 else f"({', '.join(values)})"
        ctx.code(f"return {result}")
