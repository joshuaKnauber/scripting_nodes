from random import randint
import bpy

class SocketHandler():

    def __init__(self):
        self._lookup = {
            "STRING": {
                "idname": "SN_StringSocket",
                "shape": "CIRCLE",
                "color": (0,0.75,0,1)
            },
            "BOOLEAN": {
                "idname": "SN_BoolSocket",
                "shape": "CIRCLE",
                "color": (0.65,0,0,1)
            },
            "INTEGER": {
                "idname": "SN_IntSocket",
                "shape": "CIRCLE",
                "color": (0.2,0.4,0.75,1)
            },
            "FLOAT": {
                "idname": "SN_FloatSocket",
                "shape": "CIRCLE",
                "color": (0.23,0.65,0.75,1)
            },
            "VECTOR": {
                "idname": "SN_VectorSocket",
                "shape": "CIRCLE",
                "color": (0.6,0.2,0.8,1)
            },
            "EXECUTE": {
                "idname": "SN_ExecuteSocket",
                "shape": "DIAMOND",
                "color": (1,1,1,1)
            },
            "LAYOUT": {
                "idname": "SN_LayoutSocket",
                "shape": "DIAMOND",
                "color": (0.89,0.6,0,1)
            },
            "OBJECT": {
                "idname": "SN_ObjectSocket",
                "shape": "CIRCLE",
                "color": (0,0,0,1)
            },
            "COLLECTION": {
                "idname": "SN_CollectionSocket",
                "shape": "SQUARE",
                "color": (0,0,0,1)
            },
            "DATA": {
                "idname": "SN_DataSocket",
                "shape": "CIRCLE",
                "color": (0.35,0.35,0.35,1)
            },
            "SEPARATOR": {
                "idname": "SN_SeparatorSocket",
                "shape": "SQUARE",
                "color": (1,1,1,0)
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

    def _create_socket(self,node,is_input,socket_type,label,dynamic):
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
        return self._create_socket(node,True,socket_type,label,dynamic)

    def create_output(self,node,socket_type,label,dynamic=False):
        return self._create_socket(node,False,socket_type,label,dynamic)

    def remove_input(self,node,input_socket):
        node.inputs.remove(input_socket)

    def remove_output(self,node,output_socket):
        node.outputs.remove(output_socket)

    def change_socket_type(self, node, socket, socket_type, label=""):
        if label == "":
            label = socket.name
        index = 0
        link = None
        is_input = False

        for socket_index, node_socket in enumerate(node.inputs):
            if node_socket == socket:
                is_input = True
                index = socket_index
                if len(node_socket.links):
                    link = node_socket.links[0].from_socket
        
        if not is_input:
            for socket_index, node_socket in enumerate(node.outputs):
                if node_socket == socket:
                    index = socket_index
                    if len(node_socket.links):
                        link = node_socket.links[0].to_socket

        if not is_input:
            node.outputs.remove(socket)
            out = self.create_output(node, socket_type, label)
            node.outputs.move(len(node.outputs)-1, index)
            if link:
                bpy.context.space_data.node_tree.links.new(link, out)

        else:
            node.inputs.remove(socket)
            inp = self.create_input(node, socket_type, label)
            node.inputs.move(len(node.inputs)-1, index)
            if link:
                bpy.context.space_data.node_tree.links.new(inp, link)

