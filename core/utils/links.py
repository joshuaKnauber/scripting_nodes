import bpy
from ...constants import sockets

_PREV_LINKS = {}  # {node: {socket: [next, ...]}}
_INITIALIZED = {}  # {node: bool}


def has_link_updates(node: bpy.types.Node):
    """CHecks if the node has link updates from the last stored links"""
    global _PREV_LINKS
    global _INITIALIZED
    has_updates = False
    if node.id not in _PREV_LINKS:
        _PREV_LINKS[node.id] = {}
    for socket in [*node.inputs, *node.outputs]:
        if socket not in _PREV_LINKS[node.id]:
            _PREV_LINKS[node.id][socket] = []
        if socket.get_next() != _PREV_LINKS[node.id][socket]:
            _PREV_LINKS[node.id][socket] = socket.get_next()
            has_updates = True
    has_updates = has_updates and _INITIALIZED.get(node.id, False)
    _INITIALIZED[node.id] = True
    return has_updates


def revalidate_links(ntree: bpy.types.NodeTree):
    """Validates the links of a node tree"""
    for link in ntree.links:
        link.is_valid = is_link_valid(link)


def is_link_valid(link: bpy.types.NodeLink):  # TODO
    """Checks if a link is valid"""
    from_socket = link.from_socket
    to_socket = link.to_socket

    # Invalid if connected to a disabled socket
    if getattr(to_socket, "show_editable", False) and not getattr(
        to_socket, "editable", True
    ):
        return False

    # Invalidate if two different property socket types are connected
    if (
        from_socket.bl_idname == sockets.PROPERTY
        and to_socket.bl_idname == sockets.PROPERTY
    ):
        from_type = from_socket.get_meta("type", "", True)
        to_type = to_socket.get_meta("type", "", True)
        if (from_type and to_type) and from_type != to_type:
            return False

    return True

    # def is_valid_connection(link: bpy.types.NodeLink):
    #     """Checks if the connection is valid"""
    #     connected = getattr(link.from_socket, "is_program", False) == getattr(
    #         link.to_socket, "is_program", False
    #     )
    #     program_type_a = ""
    #     for socket in [*link.from_node.inputs, *link.from_node.outputs]:
    #         if getattr(socket, "is_program", False):
    #             program_type_a = socket.bl_idname
    #             break
    #     program_type_b = ""
    #     for socket in [*link.to_node.inputs, *link.to_node.outputs]:
    #         if getattr(socket, "is_program", False):
    #             program_type_b = socket.bl_idname
    #             break
    #     return connected or (
    #         (not program_type_a or not program_type_a)
    #         or program_type_a == program_type_b
    #     )

    # def is_valid_connection_amount(link: bpy.types.NodeLink):
    #     """Checks if the connection amount is valid"""
    #     if getattr(link.from_socket, "is_program", False):
    #         return len(link.from_socket.links) <= 1
    #     elif getattr(link.to_socket, "is_program", False):
    #         return len(link.to_socket.links) <= 1
    #     return True

    # return is_valid_connection(link)
