import bpy
from ..base_node import SNA_BaseNode


class SNA_NodeGroupInputNode(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeGroupInputNode"
    bl_label = "Group Input"
    bl_width_min = 200

    def on_node_tree_update(self, ntree: bpy.types.NodeTree):
        if ntree == self.node_tree:
            print("group node update")
            self.update_sockets()

    def update_sockets(self):
        self.outputs.clear()
        for socket in self.node_tree.interface.items_tree:
            if socket.in_out == "INPUT":
                self.add_output(socket.socket_type, socket.name)
