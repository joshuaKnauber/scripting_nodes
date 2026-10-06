import bpy
from ...base_node import ScriptingBaseNode
from ._base import GroupInterfaceMixin, _poll_group_tree


class SNA_Node_GroupInput(GroupInterfaceMixin, ScriptingBaseNode, bpy.types.Node):
    """Function entry point: provides the function's parameters as outputs.

    Only appears inside group trees (is_group=True). The first output is the
    program-flow entry; subsequent outputs are the function's parameters.
    Each parameter output's socket .code is set to the parameter name so any
    downstream node inside the function body can reference it.
    """

    bl_idname = "SNA_Node_GroupInput"
    bl_label = "Group Input"

    socket_direction = "OUTPUT"
    reserved_count = 1  # the program-flow "Function" output
    default_fallback = "param"

    @classmethod
    def poll(cls, ntree):
        return _poll_group_tree(cls, ntree)

    def on_create(self):
        self.add_output("ScriptingProgramSocket", "Function")

    def generate(self):
        # Set each parameter output's code to the parameter name so the
        # function body resolves bare references like `value1` correctly.
        items = self.get_items()
        for i, item in enumerate(items):
            socket_index = i + self.reserved_count
            if socket_index < len(self.outputs):
                self.outputs[socket_index].code = item["name"]
