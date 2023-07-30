import bpy
from uuid import uuid4
from ...utils.logging import log
from ...utils.code_generation import cleanup_code


class SN_BaseNode:
    is_sn = True
    bl_width_default = 160
    bl_width_min = 40
    bl_width_max = 5000

    bl_icon = "NONE"
    bl_label = "Node"

    id: bpy.props.StringProperty(default="")

    def set_id(self):
        self.id = uuid4().hex[:5].upper()

    last_generate_time: bpy.props.FloatProperty(default=0)

    def get_code(self):
        """ Returns the code for this node. """
        return self["code"] if "code" in self else ""

    def set_code(self, value):
        """ Formats and sets the code for this socket. Updates connected nodes if necessary. """
        value = cleanup_code(value)
        is_dirty = self.get_code() != value
        self["code"] = value
        if is_dirty:  # add dependent nodes to queue
            pass  # TODO: add dependent nodes to queue
            pass  # TODO: run code
            log(2, "Node code changed", self.name)

    code: bpy.props.StringProperty(default="", get=get_code, set=set_code)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "ScriptingNodesTree"

    # poll function for node tree pointer prop searches
    def ntree_poll(self, group):
        return group.bl_idname == "ScriptingNodesTree"

    _is_root = None

    @property
    def is_root(self):
        if self._is_root is None:
            has_input_program = any(inp.is_program for inp in self.inputs)
            has_output_program = any(out.is_program for out in self.outputs)
            self._is_root = (has_input_program or has_output_program) and not (
                has_input_program and has_output_program
            )
        return self._is_root

    @property
    def node_tree(self):
        """Returns the node tree this node lives in"""
        return self.id_data

    @property
    def random_uuid(self):
        """Returns a random uuid. Note that this is not stable and will change over time!"""
        return uuid4().hex[:5].upper()

    def generate(self, context):
        """Generates the code for this node"""
        raise NotImplementedError

    def _update(self, context=None):
        self.node_tree.add_to_queue(self)

    def on_create(self, context):
        pass

    def init(self, context):
        self.set_id()
        bpy.context.scene.sn.add_node(self)
        self.on_create(context)
        self.node_tree.add_to_queue(self)

    def copy(self, old):
        self.set_id()
        bpy.context.scene.sn.add_node(self)
        self.node_tree.add_to_queue(self)

    def free(self):
        bpy.context.scene.sn.remove_node(self.id)

    # NODE UPDATE
    def update(self):
        pass

    def insert_link(self, link):
        # program nodes regenerate from right to left
        if link.to_socket.is_program:  # TODO
            if link.from_node == self:
                log(0, f"Adding {self.name} to queue after it was linked to {link.to_node.name}")
                self.node_tree.add_to_queue(self)
        # data nodes regenerate from left to right
        else:
            if link.to_node == self:
                log(0, f"Adding {self.name} to queue after it was linked to {link.from_node.name}")
                self.node_tree.add_to_queue(self)

    def remove_link(self, from_socket, to_socket):
        if from_socket and from_socket.node == self:
            # program nodes regenerate from right to left
            if from_socket.is_program:
                log(0, f"Adding {self.name} to queue after output {from_socket.index} was unlinked")
                self.node_tree.add_to_queue(self)
        elif to_socket and to_socket.node == self:
            # data nodes regenerate from left to right
            if not to_socket.is_program:
                log(0, f"Adding {self.name} to queue after input {to_socket.index} was unlinked")
                self.node_tree.add_to_queue(self)

    # DRAW NODE
    def draw_node(self, context, layout):
        pass

    def debug_code(self, layout):
        box = layout.box()
        for line in self.code.split("\n"):
            box.label(text=line)

    def draw_buttons(self, context, layout):
        sn = context.scene.sn
        # layout.label(text=str(round(self.last_generate_time*1000, 5))+"ms")
        if sn.debug_code:
            self.debug_code(layout)
        self.draw_node(context, layout)

    # DRAW NODE PANEL
    def draw_node_panel(self, context, layout):
        pass

    def draw_buttons_ext(self, context, layout):
        self.draw_node_panel(context, layout)

    # CREATE SOCKETS
    def _add_input(self, idname, label, dynamic=False):
        socket = self.inputs.new(idname, label)
        return socket

    def _add_output(self, idname, label, dynamic=False):
        socket = self.outputs.new(idname, label)
        return socket

    def add_program_input(self, label="Program"):
        return self._add_input("SN_ProgramSocket", label)

    def add_program_output(self, label="Program"):
        return self._add_output("SN_ProgramSocket", label)

    def add_execute_input(self, label="Execute"):
        return self._add_input("SN_ExecuteSocket", label)

    def add_execute_output(self, label="Execute"):
        return self._add_output("SN_ExecuteSocket", label)

    def add_dynamic_execute_input(self, label="Execute"):
        return self._add_input("SN_ExecuteSocket", label, True)

    def add_dynamic_execute_output(self, label="Execute"):
        return self._add_output("SN_ExecuteSocket", label, True)

    def add_interface_input(self, label="Interface"):
        return self._add_input("SN_InterfaceSocket", label)

    def add_interface_output(self, label="Interface"):
        return self._add_output("SN_InterfaceSocket", label)

    def add_dynamic_interface_input(self, label="Interface"):
        return self._add_input("SN_InterfaceSocket", label, True)

    def add_dynamic_interface_output(self, label="Interface"):
        return self._add_output("SN_InterfaceSocket", label, True)

    def add_data_input(self, label="Data"):
        return self._add_input("SN_DataSocket", label)

    def add_data_output(self, label="Data"):
        return self._add_output("SN_DataSocket", label)

    def add_dynamic_data_input(self, label="Data"):
        return self._add_input("SN_DataSocket", label, True)

    def add_dynamic_data_output(self, label="Data"):
        return self._add_output("SN_DataSocket", label, True)

    def add_string_input(self, label="String"):
        return self._add_input("SN_StringSocket", label)

    def add_string_output(self, label="String"):
        return self._add_output("SN_StringSocket", label)

    def add_dynamic_string_input(self, label="String"):
        return self._add_input("SN_StringSocket", label, True)

    def add_dynamic_string_output(self, label="String"):
        return self._add_output("SN_StringSocket", label, True)

    def add_enum_input(self, label="Enum"):
        return self._add_input("SN_EnumSocket", label)

    def add_enum_output(self, label="Enum"):
        return self._add_output("SN_EnumSocket", label)

    def add_dynamic_enum_input(self, label="Enum"):
        return self._add_input("SN_EnumSocket", label, True)

    def add_dynamic_enum_output(self, label="Enum"):
        return self._add_output("SN_EnumSocket", label, True)

    def add_enum_set_input(self, label="Enum Set"):
        return self._add_input("SN_EnumSetSocket", label)

    def add_enum_set_output(self, label="Enum Set"):
        return self._add_output("SN_EnumSetSocket", label)

    def add_dynamic_enum_set_input(self, label="Enum Set"):
        return self._add_input("SN_EnumSetSocket", label, True)

    def add_dynamic_enum_set_output(self, label="Enum Set"):
        return self._add_output("SN_EnumSetSocket", label, True)

    def add_boolean_input(self, label="Boolean"):
        return self._add_input("SN_BooleanSocket", label)

    def add_boolean_output(self, label="Boolean"):
        return self._add_output("SN_BooleanSocket", label)

    def add_dynamic_boolean_input(self, label="Boolean"):
        return self._add_input("SN_BooleanSocket", label, True)

    def add_dynamic_boolean_output(self, label="Boolean"):
        return self._add_output("SN_BooleanSocket", label, True)

    def add_boolean_vector_input(self, label="Boolean Vector"):
        return self._add_input("SN_BooleanVectorSocket", label)

    def add_boolean_vector_output(self, label="Boolean Vector"):
        return self._add_output("SN_BooleanVectorSocket", label)

    def add_dynamic_boolean_vector_input(self, label="Boolean Vector"):
        return self._add_input("SN_BooleanVectorSocket", label, True)

    def add_dynamic_boolean_vector_output(self, label="Boolean Vector"):
        return self._add_output("SN_BooleanVectorSocket", label, True)

    def add_integer_input(self, label="Integer"):
        return self._add_input("SN_IntegerSocket", label)

    def add_integer_output(self, label="Integer"):
        return self._add_output("SN_IntegerSocket", label)

    def add_dynamic_integer_input(self, label="Integer"):
        return self._add_input("SN_IntegerSocket", label, True)

    def add_dynamic_integer_output(self, label="Integer"):
        return self._add_output("SN_IntegerSocket", label, True)

    def add_integer_vector_input(self, label="Integer Vector"):
        return self._add_input("SN_IntegerVectorSocket", label)

    def add_integer_vector_output(self, label="Integer Vector"):
        return self._add_output("SN_IntegerVectorSocket", label)

    def add_dynamic_integer_vector_input(self, label="Integer Vector"):
        return self._add_input("SN_IntegerVectorSocket", label, True)

    def add_dynamic_integer_vector_output(self, label="Integer Vector"):
        return self._add_output("SN_IntegerVectorSocket", label, True)

    def add_float_input(self, label="Float"):
        return self._add_input("SN_FloatSocket", label)

    def add_float_output(self, label="Float"):
        return self._add_output("SN_FloatSocket", label)

    def add_dynamic_float_input(self, label="Float"):
        return self._add_input("SN_FloatSocket", label, True)

    def add_dynamic_float_output(self, label="Float"):
        return self._add_output("SN_FloatSocket", label, True)

    def add_float_vector_input(self, label="Float Vector"):
        return self._add_input("SN_FloatVectorSocket", label)

    def add_float_vector_output(self, label="Float Vector"):
        return self._add_output("SN_FloatVectorSocket", label)

    def add_dynamic_float_vector_input(self, label="Float Vector"):
        return self._add_input("SN_FloatVectorSocket", label, True)

    def add_dynamic_float_vector_output(self, label="Float Vector"):
        return self._add_output("SN_FloatVectorSocket", label, True)

    def add_icon_input(self, label="Icon"):
        return self._add_input("SN_IconSocket", label)

    def add_icon_output(self, label="Icon"):
        return self._add_output("SN_IconSocket", label)

    def add_list_input(self, label="List"):
        return self._add_input("SN_ListSocket", label)

    def add_list_output(self, label="List"):
        return self._add_output("SN_ListSocket", label)

    def add_collection_property_input(self, label="Collection Property"):
        return self._add_input("SN_CollectionPropertySocket", label)

    def add_collection_property_output(self, label="Collection Property"):
        return self._add_output("SN_CollectionPropertySocket", label)

    def add_property_input(self, label="Property"):
        return self._add_input("SN_PropertySocket", label)

    def add_property_output(self, label="Property"):
        return self._add_output("SN_PropertySocket", label)
