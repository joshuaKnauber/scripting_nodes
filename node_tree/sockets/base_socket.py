import bpy
from .conversions import CONVERSIONS
from ...addon.properties.settings.settings import property_icons


import time


class ScriptingSocket:
    ### SOCKET GENERAL
    is_sn = True
    output_limit = 9999
    # OVERWRITE
    socket_shape = "CIRCLE"  # CIRCLE | SQUARE | DIAMOND

    def update_socket_name(self, context):
        self.node.on_socket_name_change(self)

    name: bpy.props.StringProperty(
        name="Socket Name", description="Name of this socket", update=update_socket_name
    )

    ### SOCKET OPTIONS
    # OVERWRITE
    is_program = False  # Only Interface and Execute sockets are programs
    dynamic: bpy.props.BoolProperty(
        default=False,
        name="Dynamic",
        description="If this socket adds another socket when connected",
    )
    prev_dynamic: bpy.props.BoolProperty(
        default=False,
        name="Previously Dynamic",
        description="True if this socket was previously dynamic and can now be removed",
    )

    def update_conversion(self, context):
        if self.is_linked:
            from_out = self.links[0].from_socket
            self.node.node_tree.links.remove(self.links[0])
            self.node.node_tree.links.new(from_out, self)

    convert_data: bpy.props.BoolProperty(
        default=True,
        name="Convert Data",
        description="Convert the incoming data to this sockets type",
        update=update_conversion,
    )

    def update_disabled(self, context):
        self.force_update()

    disabled: bpy.props.BoolProperty(
        default=False,
        name="Disabled",
        description="Disable this socket for this node",
        update=update_disabled,
    )

    can_be_disabled: bpy.props.BoolProperty(
        default=False,
        name="Can Be Hidden",
        description="Lets the user disable this socket which can be used for evaluation",
    )

    # OVERWRITE
    subtypes = [
        "NONE"
    ]  # possible subtypes for this data socket. Vector sockets should be seperate socket types, not subtypes (their size is a subtype)!
    subtype_values = {
        "NONE": "default_value"
    }  # the matching propertie names for this data sockets subtype

    def on_subtype_update(self):
        pass

    def get_subtype_items(self, _):
        return [(name, name, name) for name in self.subtypes]

    def update_subtype(self, _):
        self.force_update()
        self.on_subtype_update()

    subtype: bpy.props.EnumProperty(
        name="Subtype",
        description="The subtype of this socket",
        items=get_subtype_items,
        update=update_subtype,
    )

    @property
    def subtype_attr(self):
        return self.subtype_values[self.subtype]

    # INDEXING OPTIONS
    def set_hide(self, value):
        """Sets the hide value of this socket and disconnects all links if hidden"""
        if value:
            for link in self.links:
                self.node.node_tree.links.remove(link)
        self.hide = value

    def update_index_type(self, context):
        if self.indexable and self.bl_idname != self.node.socket_names[self.index_type]:
            # hide all index sockets before blend data input
            hide = self.index_type == "Property"
            for inp in self.node.inputs:
                if inp == self:
                    hide = False
                if inp.indexable:
                    inp.set_hide(hide)
            # convert socket
            self.node.convert_socket(self, self.node.socket_names[self.index_type])

    indexable: bpy.props.BoolProperty(
        default=False,
        name="Indexable",
        description="If this socket is indexable. Switches between String, Integer and Blend Data",
    )

    index_type: bpy.props.EnumProperty(
        name="Index Type",
        description="The type of index this socket indexes the property with",
        items=[
            ("String", "Name", "Name", "SYNTAX_OFF", 0),
            ("Integer", "Index", "Index", "DRIVER_TRANSFORM", 1),
            ("Property", "Property", "Property", "MONKEY", 2),
        ],
        update=update_index_type,
    )

    def update_data_type(self, context):
        if self.changeable and self.data_type != self.bl_idname:
            self.node.convert_socket(self, self.data_type)

    def get_data_type_items(self, context):
        items = []
        used_idnames = []
        for name in list(self.node.socket_names.keys())[2:]:
            if not self.node.socket_names[name] in used_idnames:
                items.append(
                    (
                        self.node.socket_names[name],
                        name,
                        name,
                        property_icons[name],
                        len(items),
                    )
                )
                used_idnames.append(self.node.socket_names[name])
        return items

    changeable: bpy.props.BoolProperty(
        default=False,
        name="Changeable",
        description="If this data socket type can be changed",
    )

    data_type: bpy.props.EnumProperty(
        name="The type this socket has right now",
        update=update_data_type,
        items=get_data_type_items,
    )

    # VARIABLE SOCKET OPTIONS

    is_variable: bpy.props.BoolProperty(
        name="Is Variable",
        description="If this socket is a variable socket that can be renamed",
    )

    ### DRAW SOCKET
    # OVERWRITE
    def draw_socket(self, context, layout, node, text, minimal=False):
        pass

    def _draw_removable_socket(self, layout, node):
        """Draws the operators for removable sockets"""
        op = layout.operator("sn.remove_socket", text="", emboss=False, icon="REMOVE")
        op.node = node.name
        op.is_output = self.is_output
        op.index = self.index

    def _draw_dynamic_socket(self, layout, node, text):
        """Draws the operators for dynamic sockets"""
        # draw socket label
        if self.is_output:
            layout.label(text=text)

        # draw add operator
        op = layout.operator("sn.add_dynamic", text="", emboss=False, icon="ADD")
        op.node = node.name
        op.is_output = self.is_output
        op.insert_above = False
        op.index = self.index

        # draw socket label
        if not self.is_output:
            layout.label(text=text)

    def _draw_prev_dynamic_socket(self, context, layout, node):
        """Draws the operators for previously dynamic sockets"""
        # draw remove socket
        self._draw_removable_socket(layout, node)

        # draw add above operator
        if context.scene.sn.insert_sockets:
            op = layout.operator(
                "sn.add_dynamic", text="", emboss=False, icon="TRIA_UP"
            )
            op.node = node.name
            op.is_output = self.is_output
            op.insert_above = True
            op.index = self.index

    def draw(self, context, layout, node, text):
        """Draws this socket"""
        sn = context.scene.sn
        text = self.name
        # draw debug text for sockets
        if sn.debug_python_sockets and self.python_value:
            if not sn.debug_selected_only or (
                sn.debug_selected_only and self.node.select
            ):
                text = self.python_value.replace("\n", " || ")
        # draw dynamic sockets
        if self.dynamic:
            self._draw_dynamic_socket(layout, node, text)
        # draw variable socket
        elif self.is_variable:
            # draw previously dynamic socket (with insert socket)
            if not self.is_output and self.prev_dynamic:
                self._draw_prev_dynamic_socket(context, layout, node)
            layout.prop(self, "name", text="")
            self.draw_socket(context, layout, node, "", minimal=True)
            # draw changeable socket
            if self.changeable:
                layout.separator()
                layout.prop(self, "data_type", icon_only=True)
            # draw previously dynamic socket (with insert socket)
            if self.is_output and self.prev_dynamic:
                self._draw_prev_dynamic_socket(context, layout, node)
        # draw normal socket
        else:
            # draw output
            if self.is_output:
                self.draw_socket(context, layout, node, text)
                # draw changeable socket
                if self.changeable:
                    layout.separator()
                    layout.prop(self, "data_type", icon_only=True)
            # draw previously dynamic socket (with insert socket)
            if self.prev_dynamic:
                self._draw_prev_dynamic_socket(context, layout, node)
            # draw inputs
            if not self.is_output:
                # draw disable icon
                if self.can_be_disabled:
                    layout.prop(
                        self,
                        "disabled",
                        icon_only=True,
                        icon="HIDE_ON" if self.disabled else "HIDE_OFF",
                        emboss=False,
                    )
                    layout = layout.row()
                    layout.enabled = not self.disabled
                # draw disabled socket
                if self.can_be_disabled and self.disabled:
                    layout.label(text=text)
                # draw enabled socket
                else:
                    self.draw_socket(context, layout, node, text)
                    # draw indexable socket
                    if self.indexable:
                        layout.prop(self, "index_type", icon_only=True)
                    # draw changeable socket
                    if self.changeable:
                        layout.separator()
                        layout.prop(self, "data_type", icon_only=True)

    ### SOCKET COLOR
    # OVERWRITE
    def get_color(self, context, node):
        return (0, 0, 0)

    def draw_color(self, context, node):
        """Draws the color of this node based on the get_color function and the status of this socket"""
        c = self.get_color(context, node)
        alpha = 1
        # if self.dynamic:
        # alpha = 0
        return (c[0], c[1], c[2], alpha)

    ### PASS CODE AND DATA
    # OVERWRITE
    default_python_value = "None"
    default_prop_value = ""

    def get_python_repr(self):
        return "None"

    def reset_value(self):
        """Resets this sockets python value back to the default"""
        self.python_value = self.default_python_value

    def _get_python(self):
        """Returns the python value for this socket"""
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
                    if self.convert_data:
                        # convert different socket types
                        if from_out.bl_label != self.bl_label:
                            value = CONVERSIONS[from_out.bl_label][self.bl_label](
                                from_out, self
                            )
                        # convert convertable subtypes of the same socket
                        elif from_out.subtype != self.subtype:
                            if from_out.subtype in CONVERSIONS[from_out.bl_label]:
                                if (
                                    self.subtype
                                    in CONVERSIONS[from_out.bl_label][from_out.subtype]
                                ):
                                    value = CONVERSIONS[from_out.bl_label][
                                        from_out.subtype
                                    ][self.subtype](from_out, self)
                    return value
                return self.get_python_repr()

    def _set_python(self, value):
        """Sets the python value of this socket if it has changed and triggers an update"""
        if self.get("python_value") == None or value != self["python_value"]:
            self["python_value"] = value
            self._trigger_update()

    def _trigger_update(self):
        """Triggers node evaluation depending on the type of this socket"""
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

    python_value: bpy.props.StringProperty(
        name="Python Value",
        description="Python representation of this sockets value",
        get=_get_python,
        set=_set_python,
    )

    def _get_value(self):
        """Returns the current value of this socket"""
        return self.get(self.subtype_attr, self.default_prop_value)

    def _set_value(self, value):
        """Sets the default value depending on the current subtype and updates the python value"""
        self[self.subtype_attr] = value
        self.python_value = self._get_python()

    def _update_value(self, _):
        """Update function for the subtype properties to force an update on the node"""
        self.force_update()

    # OVERWRITE
    default_value: bpy.props.StringProperty(
        name="Value", description="Value of this socket", get=_get_value, set=_set_value
    )

    def force_update(self):
        """Triggers an update to the connected sockets, for both data and program sockets. Used to pretend the data of this node changed"""
        self._trigger_update()

    ### CONNECTED SOCKETS
    def _get_to_sockets(self, socket, check_validity=True):
        """Recursively returns the inputs connected to the given output, skipping over reroutes"""
        to_sockets = []
        # recursively find all sockets when splitting at reroutes
        if socket.node.bl_idname == "NodeReroute":
            for link in socket.node.outputs[0].links:
                to_sockets += self._get_to_sockets(link.to_socket, check_validity)
        else:
            # check validity of connection
            if not check_validity or self.node.node_tree.is_valid_connection(
                self, socket
            ):
                to_sockets.append(socket)
        return to_sockets

    def to_sockets(self, check_validity=True):
        """Returns all inputs connected to this output, skipping over reroutes"""
        sockets = []
        for link in self.links:
            sockets += self._get_to_sockets(link.to_socket, check_validity)
        return sockets

    def from_socket(self, check_validity=True):
        """Returns the socket this input comes from skipping over reroutes"""
        if len(self.links) > 0:
            from_out = self.links[0].from_socket
            # find the first socket that is not a reroute
            while from_out.node.bl_idname == "NodeReroute":
                if len(from_out.node.inputs[0].links) > 0:
                    from_out = from_out.node.inputs[0].links[0].from_socket
                else:
                    return None
            # check connection validity
            if not check_validity or self.node.node_tree.is_valid_connection(
                from_out, self
            ):
                return from_out
        return None

    ### DYNAMIC SOCKETS
    @property
    def index(self):
        """Returns the index of this socket on the node or -1 if it can't be found"""
        for index, socket in enumerate(
            self.node.outputs if self.is_output else self.node.inputs
        ):
            if socket == self:
                return index
        return -1

    def trigger_dynamic(self, insert_above=False):
        """Adds another socket like this one after itself and turns itself into a normal socket"""
        if self.dynamic or self.prev_dynamic:
            # add new socket
            if self.is_output:
                socket = self.node._add_output(self.bl_idname, self.name)
                # move socket
                self.node.outputs.move(
                    len(self.node.outputs) - 1,
                    self.index + 1 if not insert_above else self.index,
                )
            else:
                socket = self.node._add_input(self.bl_idname, self.name)
                # move socket
                self.node.inputs.move(
                    len(self.node.inputs) - 1,
                    self.index + 1 if not insert_above else self.index,
                )
            self.node.location = self.node.location

            # set new socket
            socket.dynamic = self.dynamic
            socket.prev_dynamic = self.prev_dynamic
            socket.subtype = self.subtype
            socket.changeable = self.changeable
            socket.is_variable = self.is_variable
            socket.data_type = self.data_type
            if hasattr(socket, "passthrough_layout_type"):
                socket.passthrough_layout_type = self.passthrough_layout_type

            # set this socket
            self.dynamic = False
            self.prev_dynamic = True

            if socket.dynamic:
                self.node.on_dynamic_socket_add(self)
            else:
                self.node.on_dynamic_socket_add(socket)

            socket.node._evaluate(bpy.context)
