import bpy
from ...base_node import ScriptingBaseNode
from ._base import GroupInterfaceMixin, _poll_group_tree


class SNA_Node_GroupOutput(GroupInterfaceMixin, ScriptingBaseNode, bpy.types.Node):
    """Function exit point: collects the function's return values as inputs.

    Only appears inside group trees (is_group=True). The first input is the
    program-flow exit; subsequent inputs are the function's return values.
    The tree-level codegen walks these inputs to build the `return (...)`.
    """

    bl_idname = "SNA_Node_GroupOutput"
    bl_label = "Group Output"

    socket_direction = "INPUT"
    reserved_count = 1  # the program-flow "Function" input
    default_fallback = "result"

    @classmethod
    def poll(cls, ntree):
        return _poll_group_tree(cls, ntree)

    def on_create(self):
        self.add_input("ScriptingProgramSocket", "Function")

    def generate(self):
        # Nothing to emit here - the tree-level group codegen reads our inputs
        # to assemble the return statement of the generated function.
        pass
