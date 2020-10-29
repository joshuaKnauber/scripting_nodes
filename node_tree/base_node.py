import bpy
import addon_utils
from ..handler.socket_handler import SocketHandler



class SN_ScriptingBaseNode:

    bl_width_min = 40 # customizable
    bl_width_default = 160 # customizable
    bl_width_max = 5000 # customizable
    node_color = (0.5,0.5,0.5) # customizable

    icon: bpy.props.StringProperty(default="") # customizable

    should_be_registered = False # customizable

    min_blender_version = None
    serpens_versions = None

    docs = { # customizable
        "text": ["<orange>This node hasn't been documented yet.</>"],
        "python": []
    }

    sockets = SocketHandler()

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'

    def get_serpens_version(self):
        for addon in addon_utils.modules():
            if "SERPENS" in addon.bl_info["name"]:
                return addon.bl_info["version"]

    def is_valid_serpens_version(self):
        version = self.get_serpens_version()
        return self.serpens_versions == None or (version[0],version[1]) in self.serpens_versions

    def init(self,context):
        self.use_custom_color = True
        self.color = self.node_color

        self.inititialize(context)

    def get_socket_data(self, real_socket, link_socket, connected_attr):
        socket_data = {
            "socket": real_socket,
            "name": real_socket.name,
            "value": None,
            "connected": None,
            "code": None
        }
        errors = []
        
        if link_socket.is_linked and getattr(link_socket.links[0], connected_attr).node.bl_idname == "NodeReroute":

            reroute = getattr(link_socket.links[0], connected_attr)
            if reroute == reroute.node.inputs[0]:
                reroute = reroute.node.outputs[0]
            else:
                reroute = reroute.node.inputs[0]

            socket_data, errors = self.get_socket_data(real_socket, reroute, connected_attr)

        else:

            # data socket
            if real_socket._is_data_socket:
                socket_data["value"] = str(real_socket.get_value())
                socket_data["code"] = socket_data["value"]

                if link_socket.is_linked:
                    if getattr(link_socket.links[0], connected_attr)._is_data_socket:
                        socket_data["connected"] = getattr(link_socket.links[0], connected_attr)
                        socket_data["code"] = socket_data["connected"]

                    else:
                        errors.append({
                            "title": "Wrong connection",
                            "message": "One of the sockets of this node has a wrong socket type connected",
                            "node": self,
                            "fatal": True
                        })

            # layout, execute or object socket
            elif real_socket.bl_idname in ["SN_LayoutSocket","SN_ExecuteSocket","SN_ObjectSocket", "SN_CollectionSocket"]:
                if link_socket.is_linked:
                    if getattr(link_socket.links[0], connected_attr).bl_idname == real_socket.bl_idname:
                        socket_data["connected"] = getattr(link_socket.links[0], connected_attr)
                        socket_data["code"] = getattr(link_socket.links[0], connected_attr)

                    else:
                        errors.append({
                            "title": "Wrong connection",
                            "message": "One of the sockets of this node has a wrong socket type connected",
                            "node": self,
                            "fatal": True
                        })

        return socket_data, errors

    def get_node_data(self, tree):
        errors = []
        node_input_data = []
        node_output_data = []

        for input_socket in self.inputs:
            socket_data, socket_errors = self.get_socket_data(input_socket, input_socket, "from_socket")
            node_input_data.append(socket_data)
            errors += socket_errors

        for output_socket in self.outputs:
            socket_data, socket_errors = self.get_socket_data(output_socket, output_socket, "to_socket")
            node_output_data.append(socket_data)
            errors += socket_errors

        return {"input_data":node_input_data,"output_data":node_output_data, "node_tree":tree}, errors

    def add_dynamic_socket(self,use_inputs,socket,index,parent):
        if use_inputs:
            socket = self.sockets.create_input(self,socket.socket_type,socket.name,True)
            self.inputs.move(len(self.inputs)-1,index+1)
        else:
            socket = self.sockets.create_output(self,socket.socket_type,socket.name,True)
            self.outputs.move(len(self.outputs)-1,index+1)
        socket.dynamic_parent = parent
        return socket

    def update_dynamic(self,use_inputs):
        if use_inputs:
            sockets = self.inputs
        else:
            sockets = self.outputs

        for socket in sockets:
            if socket.dynamic and socket.dynamic_parent:
                if not socket.is_linked:
                    if use_inputs:
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
                            created_sockets.append(self.add_dynamic_socket(use_inputs,socket,index,socket.uid))
                    else:
                        created_sockets.append(self.add_dynamic_socket(use_inputs,socket,index,socket.uid))
                        
                elif socket.dynamic and socket.dynamic_parent == last_parent:
                    if not len(sockets) == index+1:
                        if sockets[index+1].dynamic_parent != last_parent:
                            created_sockets.append(self.add_dynamic_socket(use_inputs,socket,index,last_parent))
                    else:
                        created_sockets.append(self.add_dynamic_socket(use_inputs,socket,index,last_parent))

    def update_vector_sockets(self):
        for input_socket in self.inputs:
            for link in input_socket.links:
                if link.from_socket.bl_idname == "SN_VectorSocket" and link.to_socket.bl_idname == "SN_VectorSocket":
                    if link.from_socket.use_four_numbers != link.to_socket.use_four_numbers:
                        from_socket = link.from_socket
                        to_socket = link.to_socket
                        bpy.context.space_data.node_tree.links.remove(link)

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

            if input_socket.bl_idname in ["SN_ExecuteSocket","SN_LayoutSocket"]:
                if len(input_socket.links) > 0:
                    if len(input_socket.links[0].from_socket.links) > 1:
                        bpy.context.space_data.node_tree.links.remove(input_socket.links[-1])

            else:
                for link in input_socket.links:
                    if link.from_socket.bl_idname != link.to_socket.bl_idname:

                        from_socket = None
                        if hasattr(link.from_socket,"_is_data_socket"):
                            from_socket = link.from_socket
                        elif link.from_socket.node.bl_idname == "NodeReroute":
                            from_socket = link.from_socket
                            while from_socket != None and from_socket.node.bl_idname == "NodeReroute":
                                if from_socket.node.inputs[0].is_linked:
                                    from_socket = from_socket.node.inputs[0].links[0].from_socket
                                else:
                                    from_socket = None

                        if from_socket:
                            if from_socket._is_data_socket and link.to_socket._is_data_socket:
                                self.cast_link(link)
                            else:
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
        self.update_socket_connections()
        self.update_vector_sockets()

        self.update_dynamic(True)
        self.update_dynamic(False)

        self.update_node()

    def is_valid_blender_version(self):
        if not self.min_blender_version:
            return True
        else:
            version = bpy.app.version
            if version[0] > self.min_blender_version[0]:
                return True
            if version[0] == self.min_blender_version[0] and version[1] > self.min_blender_version[1]:
                return True
            if version[0] == self.min_blender_version[0] and version[1] == self.min_blender_version[1] and version[2] > self.min_blender_version[2]:
                return True
            if version == self.min_blender_version:
                return True
            return False

    def evaluate_internal(self, socket, node_data, errors):
        if not self.is_valid_blender_version():
            errors.append({
                "title": "Incompatible blender version",
                "message": "This node requires blender version "+str(self.min_blender_version).replace("(","").replace(")","").replace(" ","").replace(",","."),
                "node": self,
                "fatal": True
            })
            return {
                "blocks": [{"lines": [["pass"]], "indented": []}],
                "errors": errors 
            }

        elif not self.is_valid_serpens_version():
            errors.append({
                "title": "Incompatible Serpens version",
                "message": "This node is made for any version from "+str(self.serpens_versions)+". This might cause issues",
                "node": self,
                "fatal": False
            })

        return self.evaluate(socket, node_data, errors)



    
    ##### CUSTOMIZABLE FUNCTIONS: #####


    def inititialize(self,context):
        """ This is the function called when the node is initialized. You should create the in/outputs here """
        pass

    def draw_buttons(self,context,layout):
        """ This is where you can draw additional UI elements on the node """
        pass

    def evaluate(self, socket, node_data, errors):
        """ This is the function that gets called to convert the node into python code

            socket: The socket of this node, another node has called this node from
            input_data: Dict with content regarding the inputs
            errors: a list of errors regarding the nodes inputs

            return: Dict - 'blocks': List of Dicts containing the lists 'lines' and 'indented' which
                                    themselves contain lists with strings and sockets that make up the lines.
                                    Both lists can be contain more block dictionaries for nesting and further indenting.
                            'errors': List of Dicts containing the strings 'title' and 'message' and also the parameter 'node' which
                                    is the error causing node as well as the bool 'fatal'

        """
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }

    def get_register_block(self):
        """ Returns the register code for the node

        return: List - ["bpy.utils.register_class(Test)",...]
        """
        return []

    def get_unregister_block(self):
        """ Returns the unregister code for the node

        return: List - ["bpy.utils.unregister_class(Test)",...]
        """
        return []

    def required_imports(self):
        """ Returns a list of the required imports for this node
            
        return: List - ['bpy',...]
        """
        return ["bpy"]

    def layout_type(self):
        """ Returns the layout type of this node
        
        return: String - like 'layout', 'row', 'col', ...
        """
        return ""

    def data_type(self, output):
        """ Returns the data type of this node. Has to be a bpy.types object or an empty string and never bpy.context.active_object or similar.
            Collection recognition happens through COLLECTION and OBJECT sockets.
        
        return: String - like 'bpy.types.Object' or 'bpy.types.Bone'
        """
        return ""

    def reset_data_type(self, context):
        """ Called when a connected COLLECTION OR OBJECT socket returns a different data_type (see above). 
            Used for resetting CollectionProperties or outputs using data_type.
            If called please check if there are more COLLECTION or OBJECT sockets connected and if so call reset_data_type on that node
        
        return: None
        """
        pass

    def get_variable_line(self):
        """ Used to create properties in bpy.context.scene.sn_generated_addon_properties_UID_.
            If you want global properties just return the definition here and access it using bpy.context.scene.sn_generated_addon_properties_UID_.<your_property_name>
            Collection properties can also be created here using <your_property_name>: bpy.props.CollectionProperty(type=ArrayCollection_UID_)
            If you want to use a different type of CollectionProperty please contact us directly.
        
        return: String - like 'prop_name: bpy.props.IntProperty(name"Name")', 'my_collection: bpy.props.CollectionProperty(type=ArrayCollection_UID_)'
        """
        return ""

    def get_array_line(self):
        """ Used to set collection property values.
            return a list of strings to be written in set_variables() <- Called on file start if addon is exported and enabled
        
        return: List - like ['bpy.context.scene.sn_generated_addon_properties_UID_.my_name.add().bool = True', 'bpy.context.scene.sn_generated_addon_properties_UID_.my_name.add().bool = False']
        """
        return []

    def update_node(self):
        """runs when the node is updated by connecting sockets
        """