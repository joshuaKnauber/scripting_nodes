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
        if idname == sockets.INTERFACE:
            socket = collection.new(idname, name)
    except KeyError:
        logger.log(4, f"Invalid socket type: {idname}")
    return socket
