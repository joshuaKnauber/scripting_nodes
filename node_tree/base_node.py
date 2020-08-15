import bpy
from ..handler.socket_handler import SocketHandler

class SN_ScriptingBaseNode:
    bl_width_min = 40
    bl_width_default = 160
    bl_width_max = 5000
    node_color = (0.5,0.5,0.5)

    icon: bpy.props.StringProperty(default="")

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
                input_data["value"] = str(input_socket.get_value())
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
            elif input_socket.bl_idname in ["SN_LayoutSocket","SN_ExecuteSocket","SN_ObjectSocket", "SN_CollectionSocket"]:
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
            node_input_data.append(input_data)

        return node_input_data, errors

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

    def _average_position(self,node1,node2,new_node):
        x = (node1.location[0]+node1.width) + (node2.location[0]-node1.location[0]-node1.width)/2 - new_node.width/2
        y = (node1.location[1]+node1.height) + (node2.location[1]-node1.location[1]-node1.height)/2 - new_node.height/2
        return (x,y)

    def cast_link(self,link):
        cast_nodes = {
            "SN_StringSocket": "SN_CastStringNode",
            "SN_BoolSocket": "SN_CastBooleanNode",
            "SN_IntSocket": "SN_CastIntegerNode",
            "SN_FloatSocket": "SN_CastFloatNode",
            "SN_VectorSocket": "SN_CastVectorNode"
        }
        if link.to_socket.bl_idname in cast_nodes:
            ntree = bpy.context.space_data.node_tree
            cast = ntree.nodes.new(cast_nodes[link.to_socket.bl_idname])
            cast.location = self._average_position(link.from_node,link.to_node,cast)
            ntree.links.new(link.from_socket, cast.inputs[0])
            ntree.links.new(cast.outputs[0], link.to_socket)

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

    def draw_icon_chooser(self,layout):
        """ draws the options for choosing an icon """
        box = layout.box()
        row = box.row()
        row.operator("scripting_nodes.choose_icon",text="Icons" , icon="PRESET").node_name = self.name
        if self.icon:
            row.label(icon=self.icon,text="")
            row.operator("scripting_nodes.clear_icon",text="",icon="PANEL_CLOSE",emboss=False).node_name = self.name

    def update(self):
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

    def layout_type(self):
        return ""

    def data_type(self, output):
        return ""

    def reset_data_type(self, context):
        pass