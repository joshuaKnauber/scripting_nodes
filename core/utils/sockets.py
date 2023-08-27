import bpy

from ...constants import sockets
from ...utils import logger


def add_socket(node: bpy.types.Node, idname: str, name: str, is_output: bool) -> bpy.types.NodeSocket:
    """ Adds a socket to the node """
    socket = None
    collection = node.outputs if is_output else node.inputs
    try:
        if not name:
            name = sockets.SOCKET_NAMES[idname]
        socket = collection.new(idname, name)
    except KeyError:
        logger.error(f"Invalid socket type: {idname}")
    return socket


def get_next_sockets(socket: bpy.types.NodeSocket) -> list[bpy.types.NodeSocket]:
    """ Returns the valid connected sockets """
    next_sockets = []
    for link in socket.links:
        next = link.to_socket if socket.is_output else link.from_socket
        if next.node.bl_idname == "NodeReroute":
            next_sockets += get_next_sockets(next.node.outputs[0] if socket.is_output else next.node.inputs[0])
        else:
            next_sockets.append(next)
    # TODO validate sockets
    return next_sockets
