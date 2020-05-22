import bpy

def register_dynamic_input(self, socket_idname, socket_name):
    all_sockets = []

    for inp in self.inputs:
        if inp.bl_idname == socket_idname:
            all_sockets.append(inp.is_linked)
        else:
            all_sockets.append(True)

    for i in range(len(all_sockets)):
        if not all_sockets[i]:
            all_sockets[i] = self.inputs[i]
            
    for inp in all_sockets:
        if not inp == True:
            self.inputs.remove(inp)

    self.inputs.new(socket_idname, socket_name)


def get_input_value(self,name,socket_types):
    value = str(self.inputs[name].value)
    errors = []
    if self.inputs[name].is_linked:
        if self.inputs[name].links[0].from_socket.bl_idname in socket_types:
            value = self.inputs[name].links[0].from_socket
        else:
            errors.append("wrong_socket")
    return value, errors

def icon_list():
    return bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()

def get_types():
    types = {}
    for data in dir(bpy.data):
        if eval("type(bpy.data."+data+")") == type(bpy.data.objects):
            try:
                types[eval("bpy.data."+data+".bl_rna.name.replace('Main ','')[:-1]")] = data
            except AttributeError:
                pass
    return types
