import bpy
import functools
from uuid import uuid4


"""
- code is stored in property on node
- when a nodes data changes it calls its compile function
- when as a result of that its code changes, it triggers an update to all parent program nodes
- when a start parent node is triggered, it changes the code in the node tree
"""


class SN_ScriptingBaseNode:

    bl_width_default = 160
    bl_width_min = 40
    bl_width_max = 5000

    bl_icon = "NONE"
    bl_label = "Node"

    _colors = {
        "DEFAULT": (0.18, 0.18, 0.18),
    }
    # the default color of this node. Set this to one of the options in _colors or use a vec3
    node_color = "DEFAULT"

    # set this to true for the node if it starts a program node tree (nodes like operator, panel, ...)
    is_trigger = False

    # set this for any interface nodes that change the layout type (nodes like row, column, split, ...)
    layout_type = "layout"

    """
    NOTE: remove the concept of having a main tree for the addon. from now on one addon per file and all different trees are saved as separate files
    NOTE: store a list of registered functions in the node tree. nodes can use this to check if they need to register a function again
    NOTE: when exporting the final addon, somehow trigger compile on all nodes to get export code
    NOTE: data sockets somehow need to update their own and connected nodes
    """
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'


    @property
    def node_tree(self):
        """ Returns the node tree this node lives in """
        return self.id_data


    @property
    def uuid(self):
        """ Returnes a uid for this node. Note that this is not stable and will change over time! """
        return uuid4().hex[:5].upper()


    def node_code_changed(self, context=None):
        """ Triggers an update on all affected, program nodes connected to this node. Called when the code of the node itself changes """
        if self.is_trigger:
            print("trigger code update")
        else:
            for inp in self.inputs:
                if inp.is_program:
                    from_out = inp.from_socket()
                    if from_out:
                        from_out.python_value = self.code



    def indent(self, code, indents):
        """ Indents the given code by the given amount of indents. Use this when inserting multiline blocks into code """
        lines = code.split("\n")
        for i in range(1, len(lines)):
            lines[i] = " "*(4*indents) + lines[i]
        return "\n".join(lines)


    def _get_indents(self, line):
        """ Returns the amount of spaces at the start of the given line """
        return len(line) - len(line.lstrip())
    
    def _get_min_indent(self, code_lines):
        """ Returns the minimum indent of the given lines of text """
        min_indent = 9999
        for line in code_lines:
            if not line.isspace() and line:
                min_indent = min(min_indent, self._get_indents(line))
        return min_indent if min_indent != 9999 else 0

    def _normalize_code(self, raw_code):
        """ Normalizes the given code to the minimum indent and removes empty lines """
        lines = raw_code.split("\n")
        min_indent = self._get_min_indent(lines)
        indented = []
        for line in lines:
            new_line = line[min_indent:]
            if new_line:
                indented.append(new_line)
        return "\n".join(indented)

    def _set_code(self, raw_code):
        """ Checks if the given code is different from the current code and sets the property. If required it triggers a code update """
        normalized = self._normalize_code(raw_code)
        if self.get("code") == None or normalized != self["code"]:
            self["code"] = normalized
            self.node_code_changed()

    def _get_code(self):
        """ Returns the current code of this node """
        return self.get("code", "")

    code: bpy.props.StringProperty(name="Code",
                                    description="The current compiled code for this node",
                                    set=_set_code,
                                    get=_get_code)


    def use_imperative(self, raw_code, identifier=None):
        """Handler called to add unregister code to this node. Note that this only has an effect when called in evaluate
        raw_code: the code that should be added. It's good practise to store this in a class variable and not pass it as a string in evaluate
        indentifier: if an identifier is given the raw_code is only added if code with this identifier hasn't been added to this node tree before
        """
        pass


    def use_register(self, raw_code, identifier=None):
        """Handler called to add unregister code to this node. Note that this only has an effect when called in evaluate
        raw_code: the code that should be added. It's good practise to store this in a class variable and not pass it as a string in evaluate
        indentifier: if an identifier is given the raw_code is only added if code with this identifier hasn't been added to this node tree before
        """
        pass


    def use_unregister(self, raw_code, identifier=None):
        """Handler called to add unregister code to this node. Note that this only has an effect when called in evaluate
        raw_code: the code that should be added. It's good practise to store this in a class variable and not pass it as a string in evaluate
        indentifier: if an identifier is given the raw_code is only added if code with this identifier hasn't been added to this node tree before
        """
        pass


    def evaluate(self, context):
        """Updates this nodes code and the code of all changed data outputs
        Call this when the data of this node has changed (e.g. as the update function of properties).

        The function is also automatically called when the code of program nodes connected to the output changes and when code of data inputs of this node are changed.

        Set self.code as the last thing you do in this node!!! Set all data outputs code before or this might cause issues!
        You can store temporary code in variables in this function before you set self.code if necessary to adhere to this.
        """


    order: bpy.props.IntProperty(default=0,
                                min=0,
        	                    name="Compile Index",
                                description="Index of this node in the compile order. This will change the order the code is added to the addon files. 0 is the first node to be added",
                                update=evaluate)
    

    ### INIT NODE
    def on_create(self, context): pass

    def init(self, context):
        self.use_custom_color = True
        if str(self.node_color) in self._colors:
            self.color = self._colors[self.node_color]
        else:
            self.color = self.node_color
        self.on_create(context)


    ### COPY NODE
    def on_copy(self, node): pass

    def copy(self, node):
        self.on_copy(node)


    ### FREE NODE
    def on_free(self): pass

    def free(self):
        self.on_free()


    ### NODE UPDATE
    def on_node_update(self): pass

    def update(self):
        """ Update on node graph topology changes (adding or removing nodes and links) """
        self.on_node_update()


    ### LINK UPDATE
    def on_link_insert(self, link): pass

    def after_insert_link(self, link):
        self.on_link_insert(link)

    def insert_link(self, link):
        """ Handle creation of a link to or from the node """
        # bpy.app.timers.register(functools.partial(self.after_insert_link, link), first_interval=0.001)


    ### SOCKET VALUE UPDATE
    def on_socket_value_change(self, socket): pass

    def socket_value_change(self, socket):
        self.on_socket_value_change(socket)


    ### DRAW NODE
    def draw_node(self, context, layout): pass

    def _draw_debug_code(self, context, layout):
        pure_data = not self.code
        for socket in self.inputs.values() + self.outputs.values():
            if socket.is_program:
                pure_data = False
        if not pure_data:
            box = layout.box()
            col = box.column(align=True)
            for line in self.code.split("\n"):
                col.label(text=line)


    def draw_buttons(self, context, layout):
        if context.scene.sn.debug_python_nodes:
            self._draw_debug_code(context, layout)
        self.draw_node(context, layout)


    ### DRAW NODE PANEL
    def draw_node_panel(self, context, layout): pass

    def draw_buttons_ext(self,context,layout):
        layout.use_property_split = True
        layout.prop(self, "order")
        self.draw_node_panel(context, layout)
        

    ### CREATE SOCKETS
    def _add_input(self, idname, label, dynamic=False):
        socket = self.inputs.new(idname, label)
        # socket.dynamic = dynamic
        # socket.display_shape = socket.socket_shape
        return socket
    
    def _add_output(self, idname, label, dynamic=False):
        socket = self.outputs.new(idname, label)
        # socket.dynamic = dynamic
        # socket.display_shape = socket.socket_shape
        return socket

    def add_execute_input(self, label="Execute"): return self._add_input("SN_ExecuteSocket", label)
    def add_execute_output(self, label="Execute"): return self._add_output("SN_ExecuteSocket", label)
    def add_dynamic_execute_input(self, label="Execute"): return self._add_input("SN_ExecuteSocket", label, True)
    def add_dynamic_execute_output(self, label="Execute"): return self._add_output("SN_ExecuteSocket", label, True)

    def add_interface_input(self, label="Interface"): return self._add_input("SN_InterfaceSocket", label)
    def add_interface_output(self, label="Interface"): return self._add_output("SN_InterfaceSocket", label)
    def add_dynamic_interface_input(self, label="Interface"): return self._add_input("SN_InterfaceSocket", label, True)
    def add_dynamic_interface_output(self, label="Interface"): return self._add_output("SN_InterfaceSocket", label, True)

    def add_string_input(self, label="String"): return self._add_input("SN_StringSocket", label)
    def add_string_output(self, label="String"): return self._add_output("SN_StringSocket", label)
    def add_dynamic_string_input(self, label="String"): return self._add_input("SN_StringSocket", label, True)
    def add_dynamic_string_output(self, label="String"): return self._add_output("SN_StringSocket", label, True)

    
    
    ### ERROR HANDLING
    def add_error(self, title, description, fatal=False):
        pass



    ### INTERFACE UTIL
    @property
    def active_layout(self):
        interface_socket = self.inputs[0]
        from_out = interface_socket.from_socket()
        if from_out and from_out.bl_label == "Interface":
            return from_out.node.layout_type
        return "layout"