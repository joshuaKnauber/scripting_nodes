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
    socket_index = 0
    for i, s in enumerate(socket.node.outputs if is_output else socket.node.inputs):
        if s == socket:
            socket_index = i
            break
    # delete socket
    socket.node.outputs.remove(socket) if is_output else socket.node.inputs.remove(
        socket
    )
    # add new socket
    new_socket = add_socket(socket.node, idname, name, is_output)
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
            else:
                next_sockets.append(next)
        # TODO validate sockets
    return next_sockets
