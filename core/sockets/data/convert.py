import bpy

from ....constants import sockets


def convert_types(code: str, from_socket: bpy.types.NodeSocket, to_socket: bpy.types.NodeSocket) -> str:
    """ Converts the data type from one socket to another. """
    if to_socket.bl_idname == sockets.STRING and from_socket.bl_idname != sockets.STRING:
        return f"str({code})"
    return code
