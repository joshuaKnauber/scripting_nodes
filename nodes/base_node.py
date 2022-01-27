import bpy
from uuid import uuid4
from ..utils import normalize_code, print_debug_code, unique_collection_name
from ..node_tree.sockets.conversions import CONVERT_UTILS



class SN_ScriptingBaseNode:

    is_sn = True
    bl_width_default = 160
    bl_width_min = 40
    bl_width_max = 5000

    bl_icon = "NONE"
    bl_label = "Node"

    _colors = {
        "DEFAULT": (0.18, 0.18, 0.18),
        "PROGRAM": (0.25, 0.25, 0.25),
        "INTERFACE": ((0.2, 0.17, 0.14)),
        "STRING": (0.14, 0.17, 0.19),
        "BOOLEAN": (0.15, 0.13, 0.14),
        "ICON": (0.14, 0.17, 0.19),
        "FLOAT": (0.25, 0.25, 0.25),
        "INTEGER": (0.14, 0.19, 0.15),
        "VECTOR": (0.13, 0.13, 0.15),
        "List": (0.13, 0.13, 0.15),
        "PROPERTY": (0.12, 0.15, 0.15)
    }
    # the default color of this node. Set this to one of the options in _colors or use a vec3
    node_color = "DEFAULT"

    # set this to true for the node if it starts a program node tree (nodes like operator, panel, ...)
    is_trigger = False

    # set this for any interface nodes that change the layout type (nodes like row, column, split, ...)
    layout_type = None
    
    # optional documentation for this node displayed in the n-panel
    docs = {
        "description": "",
        "settings": "",
        "inputs": "",
        "outputs": ""
    }
    
    
    # disables evaluation, only use this when the node is being initialized
    disable_evaluation: bpy.props.BoolProperty(default=True,
                                               name="Disable Evaluation",
                                               description="If this is enabled this node won't reevaluate. This should only be used for debugging or when the node is being initialized.")
    
    
    skip_export: bpy.props.BoolProperty(default=False,
                                               name="Skip Export",
                                               description="If this is enabled this node won't be part of the exported addon.")


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'
    
    
    # poll function for node tree pointer prop searches
    def ntree_poll(self, group):
        return group.bl_idname == "ScriptingNodesTree"


    @property
    def node_tree(self):
        """ Returns the node tree this node lives in """
        return self.id_data


    @property
    def uuid(self):
        """ Returns a uid for this node. Note that this is not stable and will change over time! """
        return uuid4().hex[:5].upper()
    
    
    @property
    def collection(self):
        """ Returns the collection for the nodes of this type """
        return self.node_tree.node_refs[self.bl_idname]
    
    
    # Called by any trigger node when its code updates. Use this to catch changes to nodes that you're holding references to and modify your own values
    def on_ref_update(self, node): pass
            
            
    def trigger_ref_update(self):
        """ Triggers an update on all nodes. Every node can then check if it has a reference to this node and update it's own values accordingly """
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if hasattr(node, f"ref_{self.bl_idname}") and not node == self:
                        node.on_ref_update(self)
    
    
    def get_collection_uuid(self):
        return self.get("static_uid", "")

    # uid for finding this node in the collection. Avoid using this for things that do not need to be static, use uuid instead
    static_uid: bpy.props.StringProperty(name="Static UID",
                                    description="Unique Identifier for finding this node in the ref collection of the node tree and for use for static names in code")


    @property
    def root_nodes(self):
        """ Returns the trigger nodes that are connected to this node """
        return filter(lambda node: node.is_trigger, self._get_linked_nodes())


    def _get_linked_nodes(self, linked=None):
        """ Recursively returns a list of all nodes linked to the given node """
        if linked == None: linked = [self]
        new_linked = []

        # get all nodes connected to this nodes input
        for inp in self.inputs:
            from_out = inp.from_socket()
            if from_out and not from_out.node in linked and not from_out.node in new_linked:
                new_linked.append(from_out.node)
        
        # get all nodes connected to this nodes output
        for out in self.outputs:
            for to_inp in out.to_sockets():
                if not to_inp.node in linked and not to_inp.node in new_linked:
                    new_linked.append(to_inp.node)

        # get all nodes linked to the found nodes
        linked += new_linked
        for node in new_linked:
            linked = node._get_linked_nodes(linked)

        return linked
    
    
    def _format_paragraphs(self, code):
        """ Adjusts the spacing in the code paragraphs """
        # remove blank lines
        code = code.split("\n")
        code = list(filter(lambda line: not line.strip() == "", code))
        # add blank lines
        spaced = []
        prev_indents = 0
        for i, line in enumerate(code):
            curr_indents = len(line) - len(line.lstrip())
            # add line if less indents
            if curr_indents < prev_indents:
                spaced.append("")
            # add line if decorator
            elif line.lstrip()[0] == "@":
                spaced.append("")
            # add line before comment
            elif line.lstrip()[0] == "#":
                spaced.append("")
            spaced.append(line)
            prev_indents = curr_indents
        return "\n".join(spaced)


    def _get_import_list(self, linked=[]):
        """ Returns the imports for this node as a list of import lines """
        if not linked: linked = self._get_linked_nodes()
        import_list = []
        for node in linked:
            imports = node.code_import
            for imp in imports.split("\n"):
                imp = imp.strip()
                if imp and not imp in import_list:
                    import_list.append(imp)
        return import_list

    def _format_imports(self, linked=[]):
        """ Returns the imports for this node formatted for a python file """
        if not linked: linked = self._get_linked_nodes()
        import_list = self._get_import_list(linked)
        return "import bpy\n" + "\n".join(import_list) + "\n"


    def _format_imperative(self, linked=[]):
        """ Returns the imperative code for this node formatted for a python file """
        # TODO there can still be duplicates in here. Maybe find a good way of removing those
        if not linked: linked = self._get_linked_nodes()
        full_imperative = "\n" + CONVERT_UTILS + "\n"
        for node in linked:
            imperative = node.code_imperative
            if imperative:
                full_imperative += imperative + "\n"
        return full_imperative


    def _format_register(self, linked=[]):
        """ Returns the register code for this node formatted for a python file """
        if not linked: linked = self._get_linked_nodes()
        full_register = ""
        for node in linked:
            register = node.code_register
            if register:
                full_register += register + "\n"
        if not full_register.strip():
            full_register = "pass\n" + full_register
        return "\ndef register():\n" + self.indent(full_register, 1, 0) + "\n"


    def _format_unregister(self, linked=[]):
        """ Returns the unregister code for this node formatted for a python file """
        if not linked: linked = self._get_linked_nodes()
        full_unregister = ""
        for node in linked:
            unregister = node.code_unregister
            if unregister:
                full_unregister += unregister + "\n"
        if not full_unregister.strip():
            full_unregister = "pass\n" + full_unregister
        return "\ndef unregister():\n" + self.indent(full_unregister, 1, 0) + "\n"


    def _format_node_code(self):
        """ Formats this nodes and its connected nodes code ready to register in a separate file """
        linked = self._get_linked_nodes()
        linked = sorted(linked, key=lambda node: node.order)
        imports = self._format_imports(linked)
        imperative = self._format_imperative(linked)
        main_code = self.code
        register = self._format_register(linked)
        unregister = self._format_unregister(linked)

        run_register = "\nregister()\n"
        store_unregister = f"bpy.context.scene.sn.unregister_cache['{self.as_pointer()}'] = unregister\n"

        return imports + imperative + f"\n{main_code}\n" + register + unregister + run_register + store_unregister


    def pointer_unregister(self, pointer):
        """ Unregisters the given pointers function """
        sn = bpy.context.scene.sn
        if pointer in sn.unregister_cache:
            # run unregister
            try:
                sn.unregister_cache[pointer]()
            except Exception as error:
                print(error)
            # remove unregister function
            del sn.unregister_cache[pointer]


    def node_unregister(self):
        """ Unregisters this trigger nodes current code """
        if self.is_trigger:
            self.pointer_unregister(f"{self.as_pointer()}")
 

    def compile(self):
        """ Registers or unregisters this trigger nodes current code and stores results """
        if self.is_trigger:
            # unregister
            self.node_unregister()

            # create text file
            txt = bpy.data.texts.new("tmp_serpens")
            code = self._format_node_code()
            txt.write(code)
            print_debug_code(code)

            # run text file
            ctx = bpy.context.copy()
            ctx['edit_text'] = txt
            try:
                bpy.ops.text.run_script(ctx)
            except Exception as error:
                print("")
                print(f"--- Serpens error in node tree of '{self.name}' ---")
                print(error)
                print("----------------------------------------------------")
                print("")
                if bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.keep_last_error_file:
                    if not "serpens_error" in bpy.data.texts:
                        bpy.data.texts.new("serpens_error")
                    err = bpy.data.texts["serpens_error"]
                    err.clear()
                    err.write(code)

            # remove text file
            bpy.data.texts.remove(txt)


    def _node_code_changed(self):
        """ Triggers an update on all affected, program nodes connected to this node. Called when the code of the node itself changes """
        print(f"Serpens Log: {self.label if self.label else self.name} received an update")
        if self.is_trigger:
            self.compile()
            self.trigger_ref_update()
        else:
            # update the code of all program inputs to reflect the nodes code
            for inp in self.inputs:
                if inp.is_program:
                    inp.python_value = self.code


    def _trigger_root_nodes(self):
        """ Compiles the root node of this node if it exists """
        print(f"Serpens Log: {self.label if self.label else self.name} received an update")
        roots = self.root_nodes
        for root in roots:
            root.compile()


    def indent(self, code, indents, start_line_index=1):
        """ Indents the given code by the given amount of indents. Use this when inserting multiline blocks into code """
        # join code blocks if given
        if type(code) == list:
            code = "\n".join(code)

        # split code and indent properly
        lines = code.split("\n")
        for i in range(start_line_index, len(lines)):
            lines[i] = " "*(4*indents) + lines[i]
        return "\n".join(lines)


    def _set_any_code(self, key, raw_code):
        """ Checks if the given code is different from the current code. If required it triggers a code update """
        normalized = normalize_code(raw_code)
        normalized = self._format_paragraphs(normalized)
        if self.get(key) == None or normalized != self[key]:
            self[key] = normalized

    def _set_code(self, raw_code): self._set_any_code("code", raw_code)
    def _set_code_import(self, raw_code): self._set_any_code("code_import", raw_code)
    def _set_code_imperative(self, raw_code): self._set_any_code("code_imperative", raw_code)
    def _set_code_register(self, raw_code): self._set_any_code("code_register", raw_code)
    def _set_code_unregister(self, raw_code): self._set_any_code("code_unregister", raw_code)


    def _get_code(self): return self.get("code", "")
    def _get_code_import(self): return self.get("code_import", "")
    def _get_code_imperative(self): return self.get("code_imperative", "")
    def _get_code_register(self): return self.get("code_register", "")
    def _get_code_unregister(self): return self.get("code_unregister", "")


    code: bpy.props.StringProperty(name="Code",
                                    description="The current compiled code for this node",
                                    set=_set_code,
                                    get=_get_code)

    code_import: bpy.props.StringProperty(name="Code Import",
                                    description="The current compiled code for this nodes imports",
                                    set=_set_code_import,
                                    get=_get_code_import)

    code_imperative: bpy.props.StringProperty(name="Code Imperative",
                                    description="The current compiled code for this nodes additional imperative code",
                                    set=_set_code_imperative,
                                    get=_get_code_imperative)

    code_register: bpy.props.StringProperty(name="Code Register",
                                    description="The current compiled code for this nodes registrations",
                                    set=_set_code_register,
                                    get=_get_code_register)

    code_unregister: bpy.props.StringProperty(name="Code Unregister",
                                    description="The current compiled code for this nodes unregistrations",
                                    set=_set_code_unregister,
                                    get=_get_code_unregister)


    def _evaluate(self, context):
        """ Internal evaluate to check if changes happened and trigger the compile process """
        if self.disable_evaluation: return
        
        # keep track of code before changes
        # TODO this seems to be buggy. didn't reset the code for some node, no idea how to reproduce
        prev_code = self.code
        prev_code_import = self.code_import
        prev_code_imperative = self.code_imperative
        prev_code_register = self.code_register
        prev_code_unregister = self.code_unregister
        
        # reset code
        self.code = ""
        self.code_import = ""
        self.code_imperative = ""
        self.code_register = ""
        self.code_unregister = ""

        # evaluate node
        if bpy.context.scene.sn.is_exporting:
            self.evalute_export(bpy.context)
        else:
            self.evaluate(bpy.context)

        # trigger compiler if code changed
        other_code_changed = not (prev_code_import == self.code_import and prev_code_imperative == self.code_imperative \
                                and prev_code_register == self.code_register and prev_code_unregister == self.code_unregister)
        node_code_changed = prev_code != self.code

        # trigger compiler updates
        if node_code_changed:
            self._node_code_changed()
        if other_code_changed and not self.is_trigger:
            self._trigger_root_nodes()


    def evaluate(self, context):
        """ Updates this nodes code and the code of all changed data outputs
        The function is automatically called when the code of program nodes connected to the output changes and when code of data inputs of this node are changed.
        Call _evaluate instead of evaluate when the data of this node has changed (e.g. as the update function of properties).

        You should follow this order to update this nodes code in this function:
        - Set data outputs python_value
        - Set self.code, self.code_import, self.code_imperative, self.code_register, self.code_unregister (order doesn't matter here)

        You can do all of these or none of these, but follow the order to help the register process to work smoothly
        For adding imports, only import full modules like 'import math' instead of 'from math import radians'

        You can access your data inputs python_value and the python_value of your program outputs to use in your code.
        It's recommended to use formatted strings for making this easy to read.

        You can use self.indent("your_code_string", indents) to indent blocks of code from output python_values. This can also be a list of values.
        The indents depend on your actual python file. If there are 5 indents before your string, pass 5 to the function. Make sure you're using 4 spaces as indents for your file.
        """


    def evalute_export(self, context):
        """ Used to overwrite evaluate for exporting if required """
        self.evaluate(context)


    order: bpy.props.IntProperty(default=0,
                                min=0,
        	                    name="Compile Index",
                                description="Index of this node in the compile order. This will change the order the code is added to the addon files. 0 is the first node to be added",
                                update=_evaluate)
    

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
            
    def _create_node_collection_item(self):
        """ Creates an item in the nodes collection of this node tree for this node """
        # set a new collection uid for this node
        self.static_uid = uuid4().hex[:5].upper()
        # add a new collection if it doesn't exist yet
        if not self.bl_idname in self.node_tree.node_refs:
            collection = self.node_tree.node_refs.add()
            collection.name = self.bl_idname
        # clear unused references
        self.collection.clear_unused_refs()
        # add the node to the collection
        node_ref = self.collection.refs.add()
        node_ref.uid = self.static_uid
        node_ref.name = self.name
    
    def init(self, context):
        # create node collection item
        self._create_node_collection_item()
        # set up custom color
        self._set_node_color()
        # set up the node
        self.on_create(context)
        # evaluate node for the first time
        self.disable_evaluation = False
        self._evaluate(context)


    ### COPY NODE
    def on_copy(self, old): pass

    def copy(self, old):
        # create node collection item
        self._create_node_collection_item()
        # set up the node
        self.on_copy(old)
        # compile the node for the first time after copying
        self._evaluate(bpy.context)


    ### FREE NODE
    def on_free(self): pass
    
    def _remove_node_collection_item(self):
        """ Removes the reference item for this node from this node trees references """
        for i, ref in enumerate(self.collection.refs):
            if ref.uid == self.static_uid:
                self.collection.refs.remove(i)
                break

    def free(self):
        # remove node reference from node tree references
        self._remove_node_collection_item()
        # unregister the nodes content
        if self.is_trigger:
            self.node_unregister()
        # free node
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
            self._evaluate(bpy.context)

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
            self._evaluate(bpy.context)

    def link_remove(self, from_socket, to_socket, is_output):
        self._remove_link_layout_update(from_socket, is_output)
        self.on_link_remove(from_socket, to_socket, is_output)


    ### DRAW NODE
    def draw_node(self, context, layout): pass

    def _draw_debug_code(self, context, layout):
        """ Draws the code for this node line by line on the node """
        box = layout.box()
        box.label(text=f"Static UID: {self.static_uid}")
        for key in ["code", "code_import", "code_imperative", "code_register", "code_unregister"]:
            if getattr(self, key):
                box = layout.box()
                col = box.column(align=True)
                row = col.row()
                row.enabled = False
                row.label(text=key.replace("_", " ").title())
                for line in getattr(self, key).split("\n"):
                    col.label(text=line)

    def draw_buttons(self, context, layout):
        if context.scene.sn.debug_python_nodes:
            self._draw_debug_code(context, layout)
        self.draw_node(context, layout)


    ### DRAW NODE PANEL
    def draw_node_panel(self, context, layout): pass

    def draw_buttons_ext(self,context,layout):
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "order")
        if self.is_trigger:
            layout.prop(self, "skip_export")
        if len(self.inputs):
            layout.separator()
            for inp in self.inputs:
                if not inp.is_program:
                    layout.prop(inp, "convert_data", text=f"Convert '{inp.name}' Data")
        layout.separator()
        self.draw_node_panel(context, layout)
        

    ### CREATE SOCKETS
    def _add_input(self, idname, label, dynamic=False):
        """ Adds an input for this node. This function itself doesn't evaluate as it may be used before the node is ready """
        socket = self.inputs.new(idname, label)
        socket.dynamic = dynamic
        socket.display_shape = socket.socket_shape
        return socket
    
    def _add_output(self, idname, label, dynamic=False):
        """ Adds an output for this node. This function itself doesn't evaluate as it may be used before the node is ready """
        socket = self.outputs.new(idname, label)
        socket.dynamic = dynamic
        socket.display_shape = socket.socket_shape
        return socket
    
    
    def convert_socket(self, socket, to_idname):
        """ Converts the socket from it's current type to the given idname """
        self.disable_evaluation = True
        if socket.bl_idname != to_idname:
            index = socket.index
            if index != -1:
                # save links
                links = []
                for link in socket.links:
                    if socket.is_output:
                        links.append(link.to_socket)
                    else:
                        links.append(link.from_socket)
                # add new socket
                if socket.is_output:
                    new = self._add_output(to_idname, socket.name, socket.dynamic)
                else:
                    new = self._add_input(to_idname, socket.name, socket.dynamic)
                # set socket properties
                new.prev_dynamic = socket.prev_dynamic
                if socket.subtype in new.subtypes:
                    new.subtype = socket.subtype
                new.indexable = socket.indexable
                new.index_type = socket.index_type
                new.changeable = socket.changeable
                new.data_type = new.bl_idname
                # move socket and remove old
                if socket.is_output:
                    self.outputs.remove(socket)
                    self.outputs.move(len(self.outputs)-1, index)
                    socket = self.outputs[index]
                else:
                    self.inputs.remove(socket)
                    self.inputs.move(len(self.inputs)-1, index)
                    socket = self.inputs[index]
                # relink sockets
                for link in links:
                    self.node_tree.links.new(socket, link)
        self.disable_evaluation = False
        self._evaluate(bpy.context)
    
    
    socket_names = {
        "Execute": "SN_ExecuteSocket",
        "Interface": "SN_InterfaceSocket",
        "Data": "SN_DataSocket",
        "String": "SN_StringSocket",
        "Enum": "SN_EnumSocket",
        "Boolean": "SN_BooleanSocket",
        "Boolean Vector": "SN_BooleanVectorSocket",
        "Integer": "SN_IntegerSocket",
        "Integer Vector": "SN_IntegerVectorSocket",
        "Float": "SN_FloatSocket",
        "Float Vector": "SN_FloatVectorSocket",
        "Icon": "SN_IconSocket",
        "List": "SN_ListSocket",
        "Collection Property": "SN_CollectionPropertySocket",
        "Property": "SN_PropertySocket",
    }


    def add_execute_input(self, label="Execute"): return self._add_input("SN_ExecuteSocket", label)
    def add_execute_output(self, label="Execute"): return self._add_output("SN_ExecuteSocket", label)
    def add_dynamic_execute_input(self, label="Execute"): return self._add_input("SN_ExecuteSocket", label, True)
    def add_dynamic_execute_output(self, label="Execute"): return self._add_output("SN_ExecuteSocket", label, True)

    def add_interface_input(self, label="Interface"): return self._add_input("SN_InterfaceSocket", label)
    def add_interface_output(self, label="Interface"): return self._add_output("SN_InterfaceSocket", label)
    def add_dynamic_interface_input(self, label="Interface"): return self._add_input("SN_InterfaceSocket", label, True)
    def add_dynamic_interface_output(self, label="Interface"): return self._add_output("SN_InterfaceSocket", label, True)

    def add_data_input(self, label="Data"): return self._add_input("SN_DataSocket", label)
    def add_data_output(self, label="Data"): return self._add_output("SN_DataSocket", label)
    def add_dynamic_data_input(self, label="Data"): return self._add_input("SN_DataSocket", label, True)
    def add_dynamic_data_output(self, label="Data"): return self._add_output("SN_DataSocket", label, True)

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

    def add_boolean_vector_input(self, label="Boolean Vector"): return self._add_input("SN_BooleanVectorSocket", label)
    def add_boolean_vector_output(self, label="Boolean Vector"): return self._add_output("SN_BooleanVectorSocket", label)
    def add_dynamic_boolean_vector_input(self, label="Boolean Vector"): return self._add_input("SN_BooleanVectorSocket", label, True)
    def add_dynamic_boolean_vector_output(self, label="Boolean Vector"): return self._add_output("SN_BooleanVectorSocket", label, True)

    def add_integer_input(self, label="Integer"): return self._add_input("SN_IntegerSocket", label)
    def add_integer_output(self, label="Integer"): return self._add_output("SN_IntegerSocket", label)
    def add_dynamic_integer_input(self, label="Integer"): return self._add_input("SN_IntegerSocket", label, True)
    def add_dynamic_integer_output(self, label="Integer"): return self._add_output("SN_IntegerSocket", label, True)

    def add_integer_vector_input(self, label="Integer Vector"): return self._add_input("SN_IntegerVectorSocket", label)
    def add_integer_vector_output(self, label="Integer Vector"): return self._add_output("SN_IntegerVectorSocket", label)
    def add_dynamic_integer_vector_input(self, label="Integer Vector"): return self._add_input("SN_IntegerVectorSocket", label, True)
    def add_dynamic_integer_vector_output(self, label="Integer Vector"): return self._add_output("SN_IntegerVectorSocket", label, True)

    def add_float_input(self, label="Float"): return self._add_input("SN_FloatSocket", label)
    def add_float_output(self, label="Float"): return self._add_output("SN_FloatSocket", label)
    def add_dynamic_float_input(self, label="Float"): return self._add_input("SN_FloatSocket", label, True)
    def add_dynamic_float_output(self, label="Float"): return self._add_output("SN_FloatSocket", label, True)

    def add_float_vector_input(self, label="Float Vector"): return self._add_input("SN_FloatVectorSocket", label)
    def add_float_vector_output(self, label="Float Vector"): return self._add_output("SN_FloatVectorSocket", label)
    def add_dynamic_float_vector_input(self, label="Float Vector"): return self._add_input("SN_FloatVectorSocket", label, True)
    def add_dynamic_float_vector_output(self, label="Float Vector"): return self._add_output("SN_FloatVectorSocket", label, True)

    def add_icon_input(self, label="Icon"): return self._add_input("SN_IconSocket", label)
    def add_icon_output(self, label="Icon"): return self._add_output("SN_IconSocket", label)

    def add_list_input(self, label="List"): return self._add_input("SN_ListSocket", label)
    def add_list_output(self, label="List"): return self._add_output("SN_ListSocket", label)

    def add_collection_property_input(self, label="Collection Property"): return self._add_input("SN_CollectionPropertySocket", label)
    def add_collection_property_output(self, label="Collection Property"): return self._add_output("SN_CollectionPropertySocket", label)

    def add_property_input(self, label="Property"): return self._add_input("SN_PropertySocket", label)
    def add_property_output(self, label="Property"): return self._add_output("SN_PropertySocket", label)


    def add_input_from_property(self, prop):
        """ Creates an input from the given property """
        # get property type
        prop_type = prop.type.title()
        if prop_type == "Int":
            prop_type = "Integer"
        if getattr(prop, "is_array", False):
            prop_type = f"{prop_type} Vector"
        # add property
        if prop_type in self.socket_names:
            # dynamic enums
            if prop_type == "Enum":
                if not prop.enum_items:
                    prop_type = "String"
            inp = self._add_input(self.socket_names[prop_type], prop.name)
            # get enum items
            if prop_type == "Enum":
                inp.items = str(list(map(lambda item: item.identifier, prop.enum_items)))
                if prop.is_enum_flag:
                    inp.subtype = "ENUM_FLAG"
            # get property default
            default = prop.default
            if getattr(prop, "is_array", False):
                default = tuple([prop.default]*32)
                inp.size = prop.array_length
            if prop_type == "Enum" and prop.is_enum_flag:
                pass
            else:
                inp.default_value = default

            return inp
        return None

    
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
    string: bpy.props.StringProperty(name="String",
                                description="String value of this node",
                                update=SN_ScriptingBaseNode._evaluate) # make sure to call _evaluate when a property value changes


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