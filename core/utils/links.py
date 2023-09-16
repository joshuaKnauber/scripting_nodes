import bpy


def handle_link_insert(node: bpy.types.Node, link: bpy.types.NodeLink):
    """ Called when a link is inserted """
    bpy.app.timers.register(lambda: _link_update(node, link), first_interval=0.1)


def handle_link_remove(node: bpy.types.Node, link: bpy.types.NodeLink):
    """ Called when a link is removed """
    bpy.app.timers.register(lambda: _link_update(node, link), first_interval=0.1)


def _link_update(node: bpy.types.Node, link: bpy.types.NodeLink):
    """ Updates the node and link """
    link.is_valid = is_link_valid(link)
    node.mark_dirty()


def is_link_valid(link: bpy.types.NodeLink):
    """ Checks if a link is valid """
    def is_valid_connection(link: bpy.types.NodeLink):
        """ Checks if the connection is valid """
        return getattr(link.from_socket, "is_program", False) == getattr(link.to_socket, "is_program", False)

    def is_valid_connection_amount(link: bpy.types.NodeLink):
        """ Checks if the connection amount is valid """
        if getattr(link.from_socket, "is_program", False):
            return len(link.from_socket.links) <= 1
        elif getattr(link.to_socket, "is_program", False):
            return len(link.to_socket.links) <= 1
        return True

    return is_valid_connection(link)
