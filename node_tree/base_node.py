import bpy
from ..handler.socket_handler import SocketHandler

class SN_ScriptingBaseNode:
    bl_width_min = 40
    bl_width_default = 160
    bl_width_max = 5000
    node_color = (0.5,0.5,0.5)

    sockets = SocketHandler()
    should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'

    def inititialize(self,context):
        pass

    def init(self,context):
        self.use_custom_color = True
        self.color = self.node_color

        self.inititialize(context)

    def addon_properties(self):
        return "sn_test"

    def get_input_data(self):
        errors = []
        node_input_data = []
        for input_socket in self.inputs:
            input_data = {
                "socket": input_socket,
                "name": input_socket.name,
                "value": None,
                "connected": None,
                "code": None
            }

            # data socket
            if input_socket._is_data_socket:
                input_data["value"] = input_socket.get_value()
                input_data["code"] = input_data["value"]

                if input_socket.is_linked:
                    if input_socket.links[0].from_socket._is_data_socket:
                        input_data["connected"] = input_socket.links[0].from_socket
                        input_data["code"] = input_data["connected"]

                    else:
                        errors.append({
                            "title": "Wrong connection",
                            "message": "One of the inputs of this node has a wrong output type connected",
                            "node": self,
                            "fatal": True
                        })

            # layout, execute or object socket
            elif input_socket.bl_idname in ["SN_LayoutSocket","SN_ExecuteSocket","SN_ObjectSocket"]:
                if input_socket.is_linked:
                    if input_socket.links[0].from_socket.bl_idname == input_socket.links[0].to_socket.bl_idname:
                        input_data["connected"] = input_socket.links[0].from_socket
                        input_data["code"] = input_socket.links[0].from_socket

                    else:
                        errors.append({
                            "title": "Wrong connection",
                            "message": "One of the inputs of this node has a wrong output type connected",
                            "node": self,
                            "fatal": True
                        })

        return node_input_data, errors

    def update_shapes(self,sockets):
        for socket in sockets:
            if socket.is_linked:
                socket.display_shape = socket.display_shape.replace("_DOT","")
            else:
                if not "_DOT" in socket.display_shape:
                    socket.display_shape += "_DOT"

    def add_dynamic_socket(self,inputs,socket,index,parent):
        if inputs:
            socket = self.sockets.create_input(self,socket.socket_type,socket.name,True)
            self.inputs.move(len(self.inputs)-1,index+1)
        else:
            socket = self.sockets.create_output(self,socket.socket_type,socket.name,True)
            self.outputs.move(len(self.outputs)-1,index+1)
        socket.dynamic_parent = parent
        return socket

    def update_dynamic(self,inputs):
        if inputs:
            sockets = self.inputs
        else:
            sockets = self.outputs

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

    def cast_link(self,link):
        pass#TODO: add a cast node to the link

    def update_socket_connections(self):
        for input_socket in self.inputs:
            for link in input_socket.links:
                if link.from_socket.bl_idname != link.to_socket.bl_idname:
                    if link.from_socket._is_data_socket and link.to_socket._is_data_socket:
                        self.cast_link(link)
                    else:
                        from_socket = link.from_socket
                        to_socket = link.to_socket
                        bpy.context.space_data.node_tree.links.remove(link)
                        
                        #if from_socket.dynamic and from_socket.dynamic_parent:
                        #    from_socket.node.outputs.remove(from_socket)
                        #elif not "_DOT" in from_socket.display_shape:
                        #    from_socket.display_shape += "_DOT"
                        if not "_DOT" in to_socket.display_shape:
                            to_socket.display_shape += "_DOT"

    def update(self):
        self.update_shapes(self.inputs)
        self.update_shapes(self.outputs)

        self.update_dynamic(True)
        self.update_dynamic(False)
        for input_socket in self.inputs:
            for link in input_socket.links:
                link.from_node.update()
                
        self.update_socket_connections()

    def draw_buttons(self,context,layout):
        pass

    def evaluate(self, socket, input_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": []
        }

    def get_register_block(self):
        return []

    def get_unregister_block(self):
        return []

    def required_imports(self):
        return []

    def property_block(self):
        return ""

    def layout_type(self):
        return ""