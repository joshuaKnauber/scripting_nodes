def to_sockets(socket):
    sockets = []
    for link in socket.links:
        if link.to_node.bl_idname == "NodeReroute":
            sockets.extend(to_sockets(link.to_node.outputs[0]))
        else:
            sockets.append(link.to_socket)
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
        if link.from_node.bl_idname == "NodeReroute":
            sockets.extend(from_sockets(link.from_node.inputs[0]))
        else:
            sockets.append(link.from_socket)
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
