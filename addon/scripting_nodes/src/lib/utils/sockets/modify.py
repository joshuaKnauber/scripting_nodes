def update_socket_type(socket, new_idname):
    if socket.bl_idname == new_idname:
        return

    old_index = (
        socket.node.outputs.find(socket.name)
        if socket.is_output
        else socket.node.inputs.find(socket.name)
    )
    if old_index == -1:
        return

    if socket.is_output:
        connected = [link.to_socket for link in socket.links]
        socket.node.outputs.remove(socket)
        new = socket.node.add_output(new_idname, socket.name)
        socket.node.outputs.move(len(socket.node.outputs) - 1, old_index)
    else:
        connected = [link.from_socket for link in socket.links]
        socket.node.inputs.remove(socket)
        new = socket.node.add_input(new_idname, socket.name)
        socket.node.inputs.move(len(socket.node.inputs) - 1, old_index)

    for linked in connected:
        socket.node.node_tree.links.new(new, linked)
