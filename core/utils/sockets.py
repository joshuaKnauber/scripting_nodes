import bpy

from ...constants import sockets
from ...utils import logger
from .links import is_link_valid


def add_socket(
    node: bpy.types.Node, idname: str, name: str, is_output: bool
) -> bpy.types.NodeSocket:
    """Adds a socket to the node"""
    socket = None
    collection = node.outputs if is_output else node.inputs
    try:
        if not name:
            name = sockets.SOCKET_NAMES[idname]
        socket = collection.new(idname, name)
    except KeyError:
        logger.error(f"Invalid socket type: {idname}")
    return socket


def convert_socket_type(socket: bpy.types.NodeSocket, idname: str):
    """Converts a socket to another idname"""
    if socket.bl_idname == idname:
        return socket
    connected_sockets = socket.get_next()
    name = socket.name
    is_output = socket.is_output
    node = socket.node
    socket_index = 0
    for i, s in enumerate(socket.node.outputs if is_output else socket.node.inputs):
        if s == socket:
            socket_index = i
            break
    # delete socket
    (
        socket.node.outputs.remove(socket)
        if is_output
        else socket.node.inputs.remove(socket)
    )
    # add new socket
    new_socket = add_socket(node, idname, name, is_output)
    # move socket
    if is_output:
        new_socket.node.outputs.move(len(new_socket.node.outputs) - 1, socket_index)
    else:
        new_socket.node.inputs.move(len(new_socket.node.inputs) - 1, socket_index)
    # reconnect sockets
    for s in connected_sockets:
        new_socket.node.node_tree.links.new(s, new_socket)
    return new_socket


def get_next_sockets(socket: bpy.types.NodeSocket) -> list[bpy.types.NodeSocket]:
    """Returns the valid connected sockets"""
    next_sockets = []
    for link in socket.links:
        if is_link_valid(link):
            next = link.to_socket if socket.is_output else link.from_socket
            if next.node.bl_idname == "NodeReroute":
                next_sockets += get_next_sockets(
                    next.node.outputs[0] if socket.is_output else next.node.inputs[0]
                )
            elif getattr(next.node, "is_sn_node", False):
                next_sockets.append(next)
        # TODO validate sockets
    return next_sockets


def is_only_with_name(node: bpy.types.Node, socket: bpy.types.NodeSocket) -> bool:
    """Returns True if the socket is the only one with its name"""
    sockets = node.outputs if socket.is_output else node.inputs
    return len([s for s in sockets if s.name == socket.name]) == 1


def is_last_with_name(node: bpy.types.Node, socket: bpy.types.NodeSocket) -> bool:
    """Returns True if the socket is the last one with its name"""
    sockets = node.outputs if socket.is_output else node.inputs
    return len([s for s in sockets if s.name == socket.name]) == socket.index + 1
