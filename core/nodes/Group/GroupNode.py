import bpy

from ....core.node_tree.node_tree import ScriptingNodeTree
from ..base_node import SNA_BaseNode


class SNA_NodeGroupNode(SNA_BaseNode, bpy.types.NodeCustomGroup):
    bl_idname = "SNA_NodeGroupNode"
    bl_label = "Node Group"
    bl_width_min = 200

    def poll_tree(self, tree):
        # TODO change this if recursion should be possible
        return tree.bl_idname == ScriptingNodeTree.bl_idname and tree != self.node_tree

    def update_tree(self, context):
        self.update_sockets()

    group_tree: bpy.props.PointerProperty(
        type=bpy.types.NodeTree, poll=poll_tree, update=update_tree
    )

    def draw_node(self, context, layout):
        layout.template_ID(self, "group_tree", new="node.new_node_tree")

    def on_update(self):
        print("update")
        self.update_sockets()

    def update_sockets(self):
        if self.group_tree:
            for socket in self.group_tree.interface.items_tree:
                if socket.in_out == "INPUT":
                    self.add_input(socket.socket_type, socket.name)
                else:
                    self.add_output(socket.socket_type, socket.name)
        else:
            self.inputs.clear()
            self.outputs.clear()
