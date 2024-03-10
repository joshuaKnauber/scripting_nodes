import bpy
from bpy.types import Context, Node

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

    def on_group_tree_update(self):
        print("group node update")
        self.update_sockets()

    def update_sockets(self):
        self.inputs.clear()
        self.outputs.clear()
        # TODO reconnect links
        if self.group_tree:
            for socket in self.group_tree.interface.items_tree:
                if socket.in_out == "INPUT":
                    self.add_input(socket.socket_type, socket.name)
                else:
                    self.add_output(socket.socket_type, socket.name)
        else:
            pass

    def generate(self, context: Context, trigger: Node):
        self.code = f"""
            {self.group_tree.function_name()}()
            {self.outputs[0].get_code(3)}
        """
