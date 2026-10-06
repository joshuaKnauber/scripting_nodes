def _link_is_usable(link):
    """A link is usable iff both endpoints carry compatible socket_type
    (or one is a reroute, which is type-agnostic) and Blender hasn't
    flagged it as muted/invalid. Skipping invalid links here is what
    breaks the program<->data recursion when a user drops the wrong
    kind of node into a flow.
    """
    if getattr(link, "is_muted", False):
        return False
    if not getattr(link, "is_valid", True):
        return False
    from_type = getattr(link.from_socket, "socket_type", None)
    to_type = getattr(link.to_socket, "socket_type", None)
    # Reroute - no socket_type attr - assume usable; chain ends are checked
    # by the next hop's link validation.
    if from_type is None or to_type is None:
        return True
    return from_type == to_type


def to_sockets(socket):
    sockets = []
    for link in socket.links:
        if not _link_is_usable(link):
            continue
        if link.to_node.bl_idname == "NodeReroute":
            sockets.extend(to_sockets(link.to_node.outputs[0]))
        else:
            sockets.append(link.to_socket)
    # Endpoint type guard - catches mismatches that pass through reroutes
    # (per-link check can't tell, since reroutes have no socket_type).
    src_type = getattr(socket, "socket_type", None)
    if src_type is not None:
        sockets = [s for s in sockets if getattr(s, "socket_type", None) == src_type]
    return sockets


def to_socket(socket):
    sockets = to_sockets(socket)
    return sockets[0] if sockets else None


def to_nodes(socket):
    sockets = to_sockets(socket)
    return [socket.node for socket in sockets]


def to_node(socket):
    nodes = to_nodes(socket)
    return nodes[0] if nodes else None


def from_sockets(socket):
    sockets = []
    for link in socket.links:
        if not _link_is_usable(link):
            continue
        if link.from_node.bl_idname == "NodeReroute":
            sockets.extend(from_sockets(link.from_node.inputs[0]))
        else:
            sockets.append(link.from_socket)
    # Endpoint type guard - catches mismatches that pass through reroutes
    # (per-link check can't tell, since reroutes have no socket_type).
    src_type = getattr(socket, "socket_type", None)
    if src_type is not None:
        sockets = [s for s in sockets if getattr(s, "socket_type", None) == src_type]
    return sockets


def from_socket(socket):
    sockets = from_sockets(socket)
    return sockets[0] if sockets else None


def from_nodes(socket):
    sockets = from_sockets(socket)
    return [socket.node for socket in sockets]


def from_node(socket):
    nodes = from_nodes(socket)
    return nodes[0] if nodes else None


def dynamic_socket_by_label(node, label, is_output):
    for socket in node.outputs if is_output else node.inputs:
        if socket.label == label and socket.is_dynamic:
            return socket
    return None


def socket_index(node, socket):
    for i, s in enumerate(node.outputs if socket.is_output else node.inputs):
        if s == socket:
            return i
    return -1
