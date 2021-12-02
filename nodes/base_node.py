import bpy
from uuid import uuid4



class SN_ScriptingBaseNode:

    is_sn = True
    bl_width_default = 160
    bl_width_min = 40
    bl_width_max = 5000

    bl_icon = "NONE"
    bl_label = "Node"

    _colors = {
        "DEFAULT": (0.18, 0.18, 0.18),
        "INTERFACE": ((0.2, 0.17, 0.14)),
        "STRING": (0.14, 0.17, 0.19),
        "BOOLEAN": (0.15, 0.13, 0.14),
    }
    # the default color of this node. Set this to one of the options in _colors or use a vec3
    node_color = "DEFAULT"

    # set this to true for the node if it starts a program node tree (nodes like operator, panel, ...)
    is_trigger = False

    # set this for any interface nodes that change the layout type (nodes like row, column, split, ...)
    layout_type = None


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


    def compile(self, unregister):
        """ Registers or unregisters this trigger nodes current code and stores results """
        if not unregister:
            try:
                exec(self.code + "\nprint('test')")
            except Exception as error:
                print(error)


    def node_code_changed(self, context=None):
        """ Triggers an update on all affected, program nodes connected to this node. Called when the code of the node itself changes """
        if self.is_trigger:
            self.compile(unregister=True)
            self.compile(unregister=False)
        else:
            # update the code of all program inputs to reflect the nodes code
            for inp in self.inputs:
                if inp.is_program:
                    inp.python_value = self.code


    def indent(self, code, indents):
        """ Indents the given code by the given amount of indents. Use this when inserting multiline blocks into code """
        # join code blocks if given
        if type(code) == list:
            code = "\n".join(code)

        # split code and indent properly
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
        """ Checks if the given code is different from the current code and. If required it triggers a code update """
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


    def add_imperative(self, code):
        pass

    def add_import(self, module, keys=[], aliases=[]):
        pass

    def add_register(self, code):
        pass

    def add_unregister(self, code):
        pass


    def evaluate(self, context):
        """Updates this nodes code and the code of all changed data outputs
        Call this when the data of this node has changed (e.g. as the update function of properties).

        The function is also automatically called when the code of program nodes connected to the output changes and when code of data inputs of this node are changed.

        Set self.code as the last thing you do in this node!!! Set all data outputs code before or this will lead to issues!
        You can store temporary code in variables in this function before you set self.code if necessary to adhere to this.

        You should follow this order to add code in this function:
        - Set data outputs python_value
        - Add code with add_import, add_imperative, add_register, add_unregister (the order of these doesn't matter)
        - Set self.code

        You can do all of these or none of these, but follow the order to help the register process to work smoothly
        """


    order: bpy.props.IntProperty(default=0,
                                min=0,
        	                    name="Compile Index",
                                description="Index of this node in the compile order. This will change the order the code is added to the addon files. 0 is the first node to be added",
                                update=evaluate)
    

    ### INIT NODE
    def on_create(self, context): pass

    def _set_node_color(self):
        """ Sets the color of the node depending on the node_color """
        self.use_custom_color = True
        if str(self.node_color) in self._colors:
            self.color = self._colors[self.node_color]
        elif type(self.node_color) == tuple:
            self.color = self.node_color
        else:
            self.color = self._colors["DEFAULT"]

    def init(self, context):
        # set up custom color
        self._set_node_color()
        # set up the node
        self.on_create(context)
        # evaluate node for the first time
        self.evaluate(context)


    ### COPY NODE
    def on_copy(self, old): pass

    def copy(self, old):
        # set up the node
        self.on_copy(old)
        # evaluate the node for the first time after copying
        self.evaluate(bpy.context)


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
    def on_link_insert(self, from_socket, to_socket, is_output): pass

    def _insert_link_layout_update(self, from_socket, is_output):
        """ Updates the layout type of this node when a node with layout type gets connected """
        if not is_output and from_socket.node.layout_type:
            self.evaluate(bpy.context)

    def _insert_trigger_dynamic(self, from_socket, to_socket):
        """ Triggers dynamic sockets to add new ones """
        if from_socket and from_socket.node and from_socket.dynamic:
            from_socket.trigger_dynamic()
        if to_socket and to_socket.node and to_socket.dynamic:
            to_socket.trigger_dynamic()

    def link_insert(self, from_socket, to_socket, is_output):
        self._insert_link_layout_update(from_socket, is_output)
        self.on_link_insert(from_socket, to_socket, is_output)
        self._insert_trigger_dynamic(from_socket, to_socket)


    # (from_socket or to_socket might not have a node if it was deleted!)
    def on_link_remove(self, from_socket, to_socket, is_output): pass

    def _remove_link_layout_update(self, from_socket, is_output):
        """ Updates the layout type of this node when a connected node with layout type gets removed """
        if not is_output and not from_socket.node or (from_socket.node and from_socket.node.layout_type):
            self.evaluate(bpy.context)

    def link_remove(self, from_socket, to_socket, is_output):
        self._remove_link_layout_update(from_socket, is_output)
        self.on_link_remove(from_socket, to_socket, is_output)


    ### DRAW NODE
    def draw_node(self, context, layout): pass

    def _draw_debug_code(self, context, layout):
        # get if the node only has data sockets
        pure_data = not self.code
        for socket in self.inputs.values() + self.outputs.values():
            if socket.is_program:
                pure_data = False
        # draw code line by line
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

    def add_interface_input(self, label="Interface"): return self._add_input("SN_InterfaceSocket", label)
    def add_interface_output(self, label="Interface"): return self._add_output("SN_InterfaceSocket", label)
    def add_dynamic_interface_input(self, label="Interface"): return self._add_input("SN_InterfaceSocket", label, True)
    def add_dynamic_interface_output(self, label="Interface"): return self._add_output("SN_InterfaceSocket", label, True)

    def add_string_input(self, label="String"): return self._add_input("SN_StringSocket", label)
    def add_string_output(self, label="String"): return self._add_output("SN_StringSocket", label)
    def add_dynamic_string_input(self, label="String"): return self._add_input("SN_StringSocket", label, True)
    def add_dynamic_string_output(self, label="String"): return self._add_output("SN_StringSocket", label, True)

    def add_enum_input(self, label="Enum"): return self._add_input("SN_EnumSocket", label)
    def add_enum_output(self, label="Enum"): return self._add_output("SN_EnumSocket", label)
    def add_dynamic_enum_input(self, label="Enum"): return self._add_input("SN_EnumSocket", label, True)
    def add_dynamic_enum_output(self, label="Enum"): return self._add_output("SN_EnumSocket", label, True)

    def add_boolean_input(self, label="Boolean"): return self._add_input("SN_BooleanSocket", label)
    def add_boolean_output(self, label="Boolean"): return self._add_output("SN_BooleanSocket", label)
    def add_dynamic_boolean_input(self, label="Boolean"): return self._add_input("SN_BooleanSocket", label, True)
    def add_dynamic_boolean_output(self, label="Boolean"): return self._add_output("SN_BooleanSocket", label, True)

    
    ### ERROR HANDLING
    def add_error(self, title, description, fatal=False):
        pass


    ### INTERFACE UTIL
    @property
    def active_layout(self):
        """ Returns the last connected layout type for this node """
        for inp in self.inputs:
            if inp.bl_label == "Interface":
                from_out = inp.from_socket()
                if from_out:
                    assert from_out.node.layout_type != None, f"Layout type not set on {from_out.node.bl_label}"
                    return from_out.node.layout_type
        return "layout"



### NODE TEMPLATE
"""
import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_YourNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_YourNode"
    bl_label = "Node Name"
    node_color = "DEFAULT"

    # delete these two if you don't need them
    is_trigger = False
    layout_type = "layout"


    # avoid having properties on your nodes, expose everything to sockets if possible
    string: bpy.props.StringProperty(name="String", description="String value of this node", update=evaluate)


    def on_create(self, context):
        self.add_string_output()


    def on_copy(self, old): pass


    def on_free(self): pass


    def on_node_update(self): pass


    def on_link_insert(self, socket, link): pass


    def on_link_remove(self, socket): pass


    def evaluate(self, context):
        self.outputs[0].python_value = "# comment"
        self.code = ""


    def draw_node(self, context, layout):
        layout.prop(self, "string", text="")


    def draw_node_panel(self, context, layout): pass
"""