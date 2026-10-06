def update_socket_type(socket, new_idname):
    if socket.bl_idname == new_idname:
        return

    # Cache everything we'll need before the socket is removed — accessing
    # attributes on a removed socket's Python wrapper is undefined and crashes.
    node = socket.node
    ntree = node.node_tree
    name = socket.name
    is_output = socket.is_output
    sockets = node.outputs if is_output else node.inputs

    ntree.pause_updates = True
    try:
        old_index = sockets.find(name)
        if old_index == -1:
            return

        if is_output:
            connected = [link.to_socket for link in socket.links]
            node.outputs.remove(socket)
            new = node.add_output(new_idname, name)
            node.outputs.move(len(node.outputs) - 1, old_index)
        else:
            connected = [link.from_socket for link in socket.links]
            node.inputs.remove(socket)
            new = node.add_input(new_idname, name)
            node.inputs.move(len(node.inputs) - 1, old_index)

        for linked in connected:
            ntree.links.new(new, linked)

        node._generate()
    finally:
        ntree.pause_updates = False
