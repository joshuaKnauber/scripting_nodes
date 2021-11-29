import bpy



class ScriptingSocket:
    
    ### SOCKET GENERAL
    is_sn = True
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
        
    
    ### DRAW SOCKET
    # OVERWRITE
    def draw_socket(self, context, layout, node, text): pass

    def draw(self, context, layout, node, text):
        if context.scene.sn.debug_python_sockets:
            text = self.python_value
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


    ### PASS CODE AND DATA
    # OVERWRITE
    default_python_value = "None"
    def get_python_repr(self): return "None"


    def _get_python(self):
        if self.is_program:
            if self.is_output:
                to_socket = self.to_sockets()
                if to_socket:
                    return to_socket[0].python_value
                return self.get("python_value", self.default_python_value)
            else:
                return self.get("python_value", self.default_python_value)
        else:
            if self.is_output:
                return self.get("python_value", self.default_python_value)
            else:
                # remove is linked here in favor of checking link in from_socket
                if len(self.links) > 0:
                    if self.node.node_tree.is_valid_link(self.links[0]):
                        from_out = self.from_socket()
                        # TODO handle data conversion here
                        return from_out.python_value
                return self.get_python_repr()

    def _set_python(self, value):
        if self.get("python_value") == None or value != self["python_value"]:
            self["python_value"] = value
            self._trigger_update()

    # TODO evaluate node when it is created, maybe duplicated?
    def _trigger_update(self):
        if self.is_program:
            if self.is_output:
                self.node.evaluate(bpy.context)
            else:
                from_socket = self.from_socket()
                if from_socket:
                    from_socket.node.evaluate(bpy.context)
        else:
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
        # TODO: handle subtypes values changing
        self[self.subtype_attr] = value
        self.python_value = self._get_python()

    
    # OVERWRITE
    default_value: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            get=_get_value,
                                            set=_set_value)

    
    def force_update(self):
        """ Triggers an update to the connected sockets, for both data and program sockets. Used to pretend the data of this node changed """
        self._trigger_update()


    ### CONNECTED SOCKETS
    def _get_to_sockets(self, socket):
        to_sockets = []
        if socket.node.bl_idname == "NodeReroute":
            for link in socket.node.outputs[0].links:
                to_sockets += self._get_to_sockets(link.to_socket)
        else:
            if self.node.node_tree.is_valid_connection(self, socket):
                to_sockets.append(socket)
        return to_sockets

    def to_sockets(self):
        sockets = []
        for link in self.links:
            sockets += self._get_to_sockets(link.to_socket)

        if self.is_program and len(sockets) > 1:
            return sockets[1:]
        return sockets

    def from_socket(self):
        if len(self.links) > 0:
            from_out = self.links[0].from_socket
            while from_out.node.bl_idname == "NodeReroute":
                if len(from_out.node.inputs[0].links) > 0:
                    from_out = from_out.node.inputs[0].links[0].from_socket
                else:
                    return None
            if self.node.node_tree.is_valid_connection(from_out, self):
                return from_out
        return None