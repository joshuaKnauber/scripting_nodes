import bpy



class ScriptingSocket:
    
    ### SOCKET GENERAL
    output_limit = 9999
    # OVERWRITE
    socket_shape = "CIRCLE" # CIRCLE | SQUARE | DIAMOND


    ### SOCKET OPTIONS
    # OVERWRITE
    is_program = False # Only Interface and Execute sockets are programs
    socket_type = "" # Uniquely identifiable socket type
    dynamic = False # True if this is a dynamic socket

    # OVERWRITE
    subtypes = ["NONE"] # possible subtypes for this data socket. Vector sockets should be seperate socket types, not subtypes (their size is a subtype)!
    subtype_values = {"NONE": "default_value"} # the matching propertie names for this data sockets subtype

    def get_subtype_items(self, _): return [(name, name, name) for name in self.subtypes]
    subtype: bpy.props.EnumProperty(name="Subtype",
                                    description="The subtype of this socket",
                                    items=get_subtype_items)
    @property
    def subtype_attr(self):
        return self.subtype_values[self.subtype]
    
    ### UPDATE SOCKET
    def update_socket(self, node, link):
        pass
    
    ### DRAW SOCKET
    # OVERWRITE
    def draw_socket(self, context, layout, node, text): pass

    def draw(self, context, layout, node, text):
        self.draw_socket(context, layout, node, text)


    ### SOCKET COLOR
    # OVERWRITE
    def get_color(self, context, node): return (0,0,0)

    def draw_color(self, context, node):
        c = self.get_color(context, node)
        alpha = 1
        if self.dynamic:
            alpha = 0
        return (c[0], c[1], c[2], alpha)


    ### DATA CODE
    # OVERWRITE
    default_python_value = "None"
    def get_python_repr(self): return "None"


    def _get_python(self):
        if self.is_output:
            return self.get("python_value", self.default_python_value)
        else:
            from_out = self.from_socket()
            if from_out:
                # TODO handle data conversion here
                return from_out.python_value
            return self.get_python_repr()

    def _set_python(self, value):
        self["python_value"] = value

        if self.is_output:
            for socket in self.to_sockets():
                socket.node.evaluate(bpy.context)
        else:
            self.node.evaluate(bpy.context)

    python_value: bpy.props.StringProperty(name="Python Value",
                                            description="Python representation of this sockets value",
                                            get=_get_python,
                                            set=_set_python)

    
    def _get_value(self):
        return self.get(self.subtype_attr, '')

    def _set_value(self, value):
        self[self.subtype_attr] = value
        self.python_value = self._get_python()

    
    # OVERWRITE
    default_value: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            get=_get_value,
                                            set=_set_value)


    ### CONNECTED SOCKETS
    def _get_to_sockets(self, socket):
        to_sockets = []
        if socket.node.bl_idname == "NodeReroute":
            for link in socket.node.outputs[0].links:
                to_sockets += self._get_to_sockets(link.to_socket)
        else:
            to_sockets.append(socket)
        return to_sockets

    def to_sockets(self):
        sockets = []
        for link in self.links:
            sockets += self._get_to_sockets(link.to_socket)

        if self.is_program and len(sockets) > 1:
            # TODO think about how to invalidate links here and validate them again if necessary (also above when going through links)
            return sockets[1:]
        return sockets

    def from_socket(self):
        if self.is_linked:
            from_out = self.links[0].from_socket
            while from_out.node.bl_idname == "NodeReroute":
                if from_out.node.inputs[0].is_linked:
                    from_out = from_out.node.inputs[0].links[0].from_socket
                else:
                    return None
            return from_out
        return None

    def is_valid_link(self, link):
        # TODO: validate links and mark invalid
        return True