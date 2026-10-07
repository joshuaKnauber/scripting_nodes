import bpy

from ....sockets.spec import Flow
from ...base_node import ScriptingBaseNode
from ._base import GroupInterfaceMixin, _poll_group_tree


class SNA_Node_GroupInput(GroupInterfaceMixin, ScriptingBaseNode, bpy.types.Node):
    """Start of a group (function): its flow and parameters."""

    bl_idname = "SNA_Node_GroupInput"
    bl_label = "Group Input"
    default_fallback = "param"

    @classmethod
    def poll(cls, ntree):
        return _poll_group_tree(cls, ntree)

    def socket_specs(self):
        return [], [Flow("function", "Function")] + self.item_specs()

    # The compiler emits the group function and passes the parameters as
    # flow outputs (core/compiler.py ModuleBuilder._group_function).
