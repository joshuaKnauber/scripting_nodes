import bpy
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


    """
    NOTE: remove the concept of having a main tree for the addon. from now on one addon per file and all different trees are saved as separate files
    NOTE: store a list of registered functions in the node tree. nodes can use this to check if they need to register a function again
    NOTE: when exporting the final addon, somehow trigger compile on all nodes to get export code
    NOTE: data sockets somehow need to update their own and connected nodes
    """

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
        pass


    def _get_min_indent(self, code_lines):
        """ Returns the minimum indent of the given lines of text """
        pass

    def _normalize_code(self, raw_code):
        """ Normalizes the given code to the minimum indent """
        min_indent = self._get_min_indent(raw_code.split("\n"))
        return raw_code

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
        # test = "test"
        # self.use_imperative("""
        #                     print("some code in here")
        #                     """)
        # self.code =   f"""
        #               print("test {test}")
        #               """
        self.code = ""


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
    def on_link_insert_before(self, link): pass

    def insert_link(self, link):
        """ Handle creation of a link to or from the node """
        self.on_link_insert_before(link)


    ### SOCKET VALUE UPDATE
    def on_socket_value_change(self, socket): pass

    def socket_value_change(self, socket):
        self.on_socket_value_change(socket)


    ### DRAW NODE
    def draw_node(self, context, layout): pass

    def draw_buttons(self, context, layout):
        self.draw_node(context, layout)


    ### DRAW NODE PANEL
    def draw_node_panel(self, context, layout): pass

    def draw_buttons_ext(self,context,layout):
        layout.use_property_split = True
        layout.prop(self, "order")
        layout.label(text=self.code)
        self.draw_node_panel(context, layout)
        

    ### CREATE SOCKETS
    def _add_input(self, idname, label, dynamic=False):
        socket = self.inputs.new(idname, label)
        socket.dynamic = dynamic
        socket.display_shape = socket.socket_shape
        return socket
    
    def _add_output(self, idname, label, dynamic=False):
        socket = self.outputs.new(idname, label)
        socket.dynamic = dynamic
        socket.display_shape = socket.socket_shape
        return socket

    def add_execute_input(self, label="Execute"): return self._add_input("SN_ExecuteSocket", label)
    def add_execute_output(self, label="Execute"): return self._add_output("SN_ExecuteSocket", label)
    def add_dynamic_execute_input(self, label="Execute"): return self._add_input("SN_ExecuteSocket", label, True)
    def add_dynamic_execute_output(self, label="Execute"): return self._add_output("SN_ExecuteSocket", label, True)

    def add_string_input(self, label="String"): return self._add_input("SN_StringSocket", label)
    def add_string_output(self, label="String"): return self._add_output("SN_StringSocket", label)
    def add_dynamic_string_input(self, label="String"): return self._add_input("SN_StringSocket", label, True)
    def add_dynamic_string_output(self, label="String"): return self._add_output("SN_StringSocket", label, True)

    
    
    ### ERROR HANDLING
    def add_error(self, title, description, fatal=False):
        pass