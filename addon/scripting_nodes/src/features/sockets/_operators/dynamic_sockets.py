import bpy

from scripting_nodes.src.lib.utils.sockets.sockets import (
    dynamic_socket_by_label,
    socket_index,
)
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import node_by_id


class SNA_OT_AddDynamicSocket(bpy.types.Operator):
    bl_idname = "sna.add_dynamic_socket"
    bl_label = "Add Dynamic Socket"
    bl_description = "Add a dynamic socket to the selected node"
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    is_output: bpy.props.BoolProperty()
    socket_label: bpy.props.StringProperty()

    def execute(self, context: bpy.types.Context):
        node = node_by_id(self.node_id)
        current_socket = dynamic_socket_by_label(
            node, self.socket_label, self.is_output
        )
        index = socket_index(node, current_socket)
        if self.is_output:
            node.add_output(
                current_socket.bl_idname, current_socket.label, dynamic=True
            )
            node.outputs.move(len(node.outputs) - 1, index + 1)
        else:
            node.add_input(current_socket.bl_idname, current_socket.label, dynamic=True)
            node.inputs.move(len(node.inputs) - 1, index + 1)
        current_socket.is_removable = True
        current_socket.is_dynamic = False
        node._generate()
        return {"FINISHED"}


class SNA_OT_RemoveDynamicSocket(bpy.types.Operator):
    bl_idname = "sna.remove_dynamic_socket"
    bl_label = "Remove Dynamic Socket"
    bl_description = "Remove a dynamic socket from the selected node"
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    is_output: bpy.props.BoolProperty()
    socket_index: bpy.props.IntProperty()

    def execute(self, context: bpy.types.Context):
        node = node_by_id(self.node_id)
        socket = (
            node.outputs[self.socket_index]
            if self.is_output
            else node.inputs[self.socket_index]
        )
        if self.is_output:
            node.outputs.remove(socket)
        else:
            node.inputs.remove(socket)
        node._generate()
        return {"FINISHED"}
