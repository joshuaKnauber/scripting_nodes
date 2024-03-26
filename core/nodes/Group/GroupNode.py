from math import e
import bpy
from bpy.types import Context, Node, UILayout

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

    hide_group: bpy.props.BoolProperty(
        default=False,
        name="Hide Group",
        description="Hide the group selector from node",
    )

    def draw_node(self, context, layout):
        if not self.hide_group:
            layout.template_ID(self, "group_tree", new="node.new_node_tree")

    def draw_properties(self, context: Context, layout: UILayout):
        layout.prop(self, "hide_group")

    def on_node_tree_update(self, ntree: bpy.types.NodeTree):
        if ntree == self.group_tree:
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

    def generate(self, context: Context, trigger: Node):
        if self.group_tree:
            self.code_imports = f"from .{self.group_tree.module_name()} import {self.group_tree.function_name()}"

            inputs = ", ".join(
                [
                    (
                        socket.get_code()  # TODO properties as inputs & self for classes (probably just locals)
                        if not getattr(socket, "is_program", False)
                        else (
                            socket.get_meta("layout", "self.layout")
                            if socket.bl_idname == "SNA_InterfaceSocket"
                            else "None"
                        )
                    )
                    for socket in self.inputs
                ]
            )

            self.code = f"""
                {self.group_tree.function_name()}({inputs})
                {self.outputs[0].get_code(3)}
            """
