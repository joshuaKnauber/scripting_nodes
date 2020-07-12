from random import randint

class SocketHandler():

    def __init__(self):
        self._lookup = {
            "STRING": {
                "idname": "SN_StringSocket",
                "shape": "CIRCLE",
                "color": (0.85,0.1,0.75,1)
            },
            "EXECUTE": {
                "idname": "SN_ExecuteSocket",
                "shape": "DIAMOND",
                "color": (1,1,1,1)
            },
            "LAYOUT": {
                "idname": "SN_LayoutSocket",
                "shape": "DIAMOND",
                "color": (0.89,0.5,0,1)
            }
        }

    def _socket_types(self):
        socket_types = ""
        for socket_type in self._lookup:
            socket_types += "'" + socket_type + "',"
        if socket_types:
            socket_types = socket_types[:-1]
        return socket_types

    def _setup_socket(self,socket,socket_type,data,dynamic):
        socket.uid = str(randint(0,9999))
        socket.dynamic = dynamic
        socket.socket_type = socket_type
        socket.socket_color = data["color"]
        socket.display_shape = data["shape"]

    def create_socket(self,node,is_input,socket_type,label,dynamic):
        if not socket_type in self._lookup:
            message = "Socket type '" + socket_type + "' not in " + self._socket_types() + ""
            raise ValueError(message) 
        else:
            socket_data = self._lookup[socket_type]
            if is_input:
                socket = node.inputs.new(socket_data["idname"],label)
            else:
                socket = node.outputs.new(socket_data["idname"],label)
            self._setup_socket(socket,socket_type,socket_data,dynamic)
            return socket

    def create_input(self,node,socket_type,label,dynamic=False):
        return self.create_socket(node,True,socket_type,label,dynamic)

    def create_output(self,node,socket_type,label,dynamic=False):
        return self.create_socket(node,False,socket_type,label,dynamic)