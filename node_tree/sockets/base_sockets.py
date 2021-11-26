import bpy



class ScriptingSocket:
    
    ### SOCKET GENERAL
    output_limit = 9999
    socket_shape = "CIRCLE" # CIRCLE | SQUARE | DIAMOND


    ### SOCKET OPTIONS    
    is_program = False # Only Interface and Execute sockets are programs
    socket_type = "" # Uniquely identifiable socket type
    
    dynamic = False # True if this is a dynamic socket

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
    def draw(self, context, layout, node, text):
        self.draw_socket(context, layout, node, text)


    ### SOCKET COLOR
    def get_color(self, context, node):
        """ overwrite this to set the sockets basic color """
        return (0,0,0)

    def draw_color(self, context, node):
        c = self.get_color(context, node)
        alpha = 1
        if self.dynamic:
            alpha = 0
        return (c[0], c[1], c[2], alpha)


    ### HANDLE DATA CODE
    def to_sockets(self):
        sockets = []
        for link in self.links:
            if self.is_valid_link(link):
                to_inp = self.to_socket(link)
                if to_inp:
                    sockets.append(to_inp)
        return sockets

    def to_socket(self, link):
        if self.is_linked:
            to_inp = link.to_socket
            while to_inp.node.bl_idname == "NodeReroute":
                if to_inp.node.outputs[0].is_linked:
                    # BUG what if routing in multiple directions again?
                    to_inp = to_inp.node.outputs[0].links[0].to_socket
                else:
                    return None
            return to_inp
        return None

    def from_socket(self):
        if self.is_linked:
            from_out = self.links[0].from_socket
            while from_out.node.bl_idname == "NodeReroute":
                if from_out.node.inputs[0].is_linked:
                    # BUG see to_socket
                    from_out = from_out.node.inputs[0].links[0].from_socket
                else:
                    return None
            return from_out
        return None

    def is_valid_link(self, link):
        # TODO: validate links and mark invalid
        return True