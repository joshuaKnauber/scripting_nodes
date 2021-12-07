import bpy
from .conversions import CONVERSIONS



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
    dynamic: bpy.props.BoolProperty(default=False,
                                    name="Dynamic",
                                    description="If this socket adds another socket when connected")
    prev_dynamic: bpy.props.BoolProperty(default=False,
                                    name="Previously Dynamic",
                                    description="True if this socket was previously dynamic and can now be removed")

    # OVERWRITE
    subtypes = ["NONE"] # possible subtypes for this data socket. Vector sockets should be seperate socket types, not subtypes (their size is a subtype)!
    subtype_values = {"NONE": "default_value"} # the matching propertie names for this data sockets subtype

    def get_subtype_items(self, _): return [(name, name, name) for name in self.subtypes]
    def update_subtype(self, _): self.force_update()
    subtype: bpy.props.EnumProperty(name="Subtype",
                                    description="The subtype of this socket",
                                    items=get_subtype_items,
                                    update=update_subtype)
    @property
    def subtype_attr(self):
        return self.subtype_values[self.subtype]
        
    
    ### DRAW SOCKET
    # OVERWRITE
    def draw_socket(self, context, layout, node, text): pass

    def _draw_removable_socket(self, layout, node):
        """ Draws the operators for removable sockets """
        op = layout.operator("sn.remove_socket", text="", emboss=False, icon="REMOVE")
        op.node = node.name
        op.is_output = self.is_output
        op.index = self.index

    def _draw_dynamic_socket(self, layout, node, text):
        """ Draws the operators for dynamic sockets """
        # draw add operator
        op = layout.operator("sn.add_dynamic", text="", emboss=False, icon="ADD")
        op.node = node.name
        op.is_output = self.is_output
        op.insert_above = False
        op.index = self.index

        # draw socket label
        layout.label(text=text)

    def _draw_prev_dynamic_socket(self, context, layout, node):
        """ Draws the operators for previously dynamic sockets """
        # draw remove socket
        self._draw_removable_socket(layout, node)

        # draw add above operator
        if context.scene.sn.insert_sockets:
            op = layout.operator("sn.add_dynamic", text="", emboss=False, icon="TRIA_UP")
            op.node = node.name
            op.is_output = self.is_output
            op.insert_above = True
            op.index = self.index

    def draw(self, context, layout, node, text):
        """ Draws this socket """
        # draw debug text for sockets
        if context.scene.sn.debug_python_sockets and self.python_value:
            text = self.python_value.replace("\n", " || ")
        if self.dynamic:
            self._draw_dynamic_socket(layout, node, text)
        else:
            if self.prev_dynamic:
                self._draw_prev_dynamic_socket(context, layout, node)
            self.draw_socket(context, layout, node, text)


    ### SOCKET COLOR
    # OVERWRITE
    def get_color(self, context, node): return (0,0,0)

    def draw_color(self, context, node):
        """ Draws the color of this node based on the get_color function and the status of this socket """
        c = self.get_color(context, node)
        alpha = 1
        if self.dynamic:
            alpha = 0
        return (c[0], c[1], c[2], alpha)


    ### PASS CODE AND DATA
    # OVERWRITE
    default_python_value = "None"
    default_prop_value = ""
    def get_python_repr(self): return "None"


    def _get_python(self):
        """ Returns the python value for this socket """
        if self.is_program:
            if self.is_output:
                # returns the connected program inputs python value or this sockets default
                to_socket = self.to_sockets()
                if to_socket:
                    return to_socket[0].python_value
                return self.get("python_value", self.default_python_value)
            else:
                # returns this program inputs python value or its default
                return self.get("python_value", self.default_python_value)
        else:
            if self.is_output:
                # returns this data outputs current python value or its default
                return self.get("python_value", self.default_python_value)
            else:
                # returns the connected data outputs current python value or the python representation for this input
                from_out = self.from_socket()
                if from_out:
                    value = from_out.python_value
                    if from_out.bl_label != self.bl_label:
                        value = CONVERSIONS[from_out.bl_label][self.bl_label](value)
                    return value
                return self.get_python_repr()


    def _set_python(self, value):
        """ Sets the python value of this socket if it has changed and triggers an update """
        if self.get("python_value") == None or value != self["python_value"]:
            self["python_value"] = value
            self._trigger_update()


    def _trigger_update(self):
        """ Triggers node evaluation depending on the type of this socket """
        if self.is_program:
            # evaluate this node if this is a program output
            if self.is_output:
                self.node._evaluate(bpy.context)
            # evaluate all connected nodes if this is a program input
            else:
                from_socket = self.from_socket()
                if from_socket:
                    from_socket.node._evaluate(bpy.context)
        else:
            # evaluate all connected nodes if this is a data output
            if self.is_output:
                for socket in self.to_sockets():
                    socket.node._evaluate(bpy.context)
            # evaluate this node if this is a data input
            else:
                self.node._evaluate(bpy.context)
        

    python_value: bpy.props.StringProperty(name="Python Value",
                                            description="Python representation of this sockets value",
                                            get=_get_python,
                                            set=_set_python)

    
    def _get_value(self):
        """ Returns the current value of this socket """
        return self.get(self.subtype_attr, self.default_prop_value)


    def _set_value(self, value):
        """ Sets the default value depending on the current subtype and updates the python value """
        self[self.subtype_attr] = value
        self.python_value = self._get_python()


    def _update_value(self, _):
        """ Update function for the subtype properties to force an update on the node """
        self.force_update()

    
    # OVERWRITE
    default_value: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            get=_get_value,
                                            set=_set_value)

    
    def force_update(self):
        """ Triggers an update to the connected sockets, for both data and program sockets. Used to pretend the data of this node changed """
        self._trigger_update()


    ### CONNECTED SOCKETS
    def _get_to_sockets(self, socket, check_validity=True):
        """ Recursively returns the inputs connected to the given output, skipping over reroutes  """
        to_sockets = []
        # recursively find all sockets when splitting at reroutes
        if socket.node.bl_idname == "NodeReroute":
            for link in socket.node.outputs[0].links:
                to_sockets += self._get_to_sockets(link.to_socket, check_validity)
        else:
            # check validity of connection
            if not check_validity or self.node.node_tree.is_valid_connection(self, socket):
                to_sockets.append(socket)
        return to_sockets

    def to_sockets(self, check_validity=True):
        """ Returns all inputs connected to this output, skipping over reroutes """
        sockets = []
        for link in self.links:
            sockets += self._get_to_sockets(link.to_socket, check_validity)
        return sockets


    def from_socket(self, check_validity=True):
        """ Returns the socket this input comes from skipping over reroutes """
        if len(self.links) > 0:
            from_out = self.links[0].from_socket
            # find the first socket that is not a reroute
            while from_out.node.bl_idname == "NodeReroute":
                if len(from_out.node.inputs[0].links) > 0:
                    from_out = from_out.node.inputs[0].links[0].from_socket
                else:
                    return None
            # check connection validity
            if not check_validity or self.node.node_tree.is_valid_connection(from_out, self):
                return from_out
        return None


    ### DYNAMIC SOCKETS
    @property
    def index(self):
        """ Returns the index of this socket on the node or -1 if it can't be found """
        for index, socket in enumerate(self.node.outputs if self.is_output else self.node.inputs):
            if socket == self:
                return index
        return -1

    def trigger_dynamic(self, insert_above=False):
        """ Adds another socket like this one after itself and turns itself into a normal socket """
        if self.dynamic or self.prev_dynamic:
            # add new socket
            if self.is_output:
                socket = self.node._add_output(self.bl_idname, self.name)
                # move socket
                self.node.outputs.move(len(self.node.outputs)-1, self.index+1 if not insert_above else self.index)
            else:
                socket = self.node._add_input(self.bl_idname, self.name)
                # move socket
                self.node.inputs.move(len(self.node.inputs)-1, self.index+1 if not insert_above else self.index)

            # set new socket
            socket.dynamic = self.dynamic
            socket.prev_dynamic = self.prev_dynamic
            socket.subtype = self.subtype

            # set this socket
            self.dynamic = False
            self.prev_dynamic = True