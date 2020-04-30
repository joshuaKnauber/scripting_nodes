
def register_dynamic_input(self, socket_idname, socket_name):
    all_sockets = []

    for inp in self.inputs:
        if inp.bl_idname == socket_idname:
            all_sockets.append(inp.is_linked)
        else:
            all_sockets.append(True)

    for i in range(len(all_sockets)):
        if not all_sockets[i]:
            self.inputs.remove(self.inputs[i])
    self.inputs.new(socket_idname, socket_name)