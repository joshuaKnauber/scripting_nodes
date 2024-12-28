from scripting_nodes.src.features.node_tree.node_tree import ScriptingNodeTree
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_GroupOutput(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_GroupOutput"
    bl_label = "Group Output"

    def generate(self):
        pass

    def on_group_socket_change(self, tree):
        self.inputs.clear()
        for socket in tree.interface.items_tree:
            if socket.in_out == "OUTPUT":
                self.add_input(socket.socket_type, socket.name)
        self._generate()
