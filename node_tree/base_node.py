import bpy
from ..handler.socket_handler import SocketHandler

class SN_ScriptingBaseNode:
    bl_width_min = 40
    bl_width_default = 160
    bl_width_max = 5000
    node_color = (0.5,0.5,0.5)

    sockets = SocketHandler()

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'

    def inititialize(self,context):
        pass

    def init(self,context):
        self.sockets._node = self

        self.use_custom_color = True
        self.color = self.node_color

        self.inititialize(context)

    def update_shapes(self,sockets):
        for socket in sockets:
            if socket.is_linked:
                socket.display_shape = socket.display_shape.replace("_DOT","")
            else:
                if not "_DOT" in socket.display_shape:
                    socket.display_shape += "_DOT"

    def add_dynamic_socket(self,inputs,socket,index,parent):
        if inputs:
            socket = self.sockets.create_input(socket.socket_type,socket.name,True)
            self.inputs.move(len(self.inputs)-1,index+1)
        else:
            socket = self.sockets.create_output(socket.socket_type,socket.name,True)
            self.outputs.move(len(self.outputs)-1,index+1)
        socket.dynamic_parent = parent
        return socket

    def update_dynamic(self,sockets,inputs):
        for socket in sockets:
            if socket.dynamic and socket.dynamic_parent:
                if not socket.is_linked:
                    if inputs:
                        self.inputs.remove(socket)
                    else:
                        self.outputs.remove(socket)

        last_parent = "null"
        created_sockets = []
        for index, socket in enumerate(sockets):
            if not socket in created_sockets:
                if socket.dynamic and not socket.dynamic_parent:
                    last_parent = socket.uid

                if socket.dynamic and not socket.dynamic_parent and socket.is_linked:
                    if not len(sockets) == index+1:
                        if sockets[index+1].dynamic_parent != socket.uid:
                            created_sockets.append(self.add_dynamic_socket(inputs,socket,index,socket.uid))
                    else:
                        created_sockets.append(self.add_dynamic_socket(inputs,socket,index,socket.uid))
                        
                elif socket.dynamic and socket.dynamic_parent == last_parent:
                    if not len(sockets) == index+1:
                        if sockets[index+1].dynamic_parent != last_parent:
                            created_sockets.append(self.add_dynamic_socket(inputs,socket,index,last_parent))
                    else:
                        created_sockets.append(self.add_dynamic_socket(inputs,socket,index,last_parent))

    def update(self):
        self.update_shapes(self.inputs)
        self.update_shapes(self.outputs)

        self.update_dynamic(self.inputs,True)
        self.update_dynamic(self.outputs,False)
        for input_socket in self.inputs:
            for link in input_socket.links:
                link.from_node.update()

    def evaluate(self, socket, input_data):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines

                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines

                    ]
                }
            ],
            "errors": [
                {
                    "error": "",
                    "node": self,
                    "socket": None
                }
            ]
        }

    def get_register_block(self):
        return []

    def get_unregister_block(self):
        return []

    def required_imports(self):
        return []

    def layout_type(self):
        return "layout"