import bpy
from bpy.types import Context, Node, UILayout

from ....utils.classes import extend_blender_class

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
            layout.template_ID(self, "group_tree", new="sna.add_group_nodetree")

    def draw_properties(self, context: Context, layout: UILayout):
        layout.prop(self, "hide_group")

    def on_node_tree_update(self, ntree: bpy.types.NodeTree):
        if ntree == self.group_tree:
            self.update_sockets()

    def update_sockets(self):
        if self.group_tree:
            # remember links
            inpLinks = {}
            outLinks = {}
            for socket in self.inputs:
                for link in socket.links:
                    inpLinks[link.from_socket] = (socket.name, socket.bl_idname)
            for socket in self.outputs:
                for link in socket.links:
                    outLinks[link.to_socket] = (socket.name, socket.bl_idname)
            # clear inputs and outputs
            self.inputs.clear()
            self.outputs.clear()
            # add inputs and outputs
            for socket in self.group_tree.interface.items_tree:
                if socket.in_out == "INPUT":
                    self.add_input(socket.socket_type, socket.name)
                if socket.in_out == "OUTPUT":
                    self.add_output(socket.socket_type, socket.name)
            # reconnect links
            for from_socket, to_socket in inpLinks.items():
                to_socket = next(
                    filter(
                        lambda inp: inp.name == to_socket[0]
                        and inp.bl_idname == to_socket[1],
                        self.inputs,
                    )
                )
                if to_socket:
                    from_socket.node.node_tree.links.new(to_socket, from_socket)
            for to_socket, from_socket in outLinks.items():
                from_socket = next(
                    filter(
                        lambda out: out.name == from_socket[0]
                        and out.bl_idname == from_socket[1],
                        self.outputs,
                    )
                )
                if from_socket:
                    to_socket.node.node_tree.links.new(from_socket, to_socket)
        self.mark_dirty()

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


@extend_blender_class
class NodeGroupInput(bpy.types.NodeGroupInput):
    @property
    def node_tree(self):
        return self.id_data


@extend_blender_class
class NodeGroupOutput(bpy.types.NodeGroupOutput):
    @property
    def node_tree(self):
        return self.id_data
