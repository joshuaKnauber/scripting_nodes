import bpy
from .sockets import add_to_remove_links
from ..compiler.compiler import combine_blocks



class SN_ScriptingBaseNode:

    bl_width_default = 160
    bl_width_min = 40
    bl_width_max = 5000

    bl_icon = "NONE"
    bl_label = "Node"
    
    node_options = {
        "starts_tree": False,
        "default_color": (1,0,1),
        "import_once": False,
        "evaluate_once": False,
        "register_once": False,
        "unregister_once": False,
        "imperative_once": False,
    }
    
    node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'
    
    def update_needs_compile(self,context):
        self.node_tree.set_changes(True)


    ### INIT NODE
    def on_create(self,context): pass


    def init(self,context):
        self.node_tree = self.id_data
        self.node_tree.set_changes(True)
        self.color = self.node_options["default_color"]
        self.use_custom_color = True
        self.on_create(context)


    ### COPY NODE
    def on_copy(self,node): pass


    def copy(self,node):
        self.node_tree = self.id_data
        self.node_tree.set_changes(True)
        self.on_copy(node)


    ### FREE NODE
    def on_free(self): pass


    def free(self):
        self.node_tree.set_changes(True)
        self.on_free()


    ### NODE UPDATE
    def on_node_update(self): pass


    def update(self):
        self.node_tree.set_changes(True)
        self.on_node_update()


    ### SOCKET UPDATE
    # def on_socket_update(self): pass


    # def socket_value_update(self, context):
    #     self.node_tree.set_changes(True)
    #     self.on_socket_update()


    ### LINK UPDATE
    def on_link_insert(self,link): pass


    def insert_link(self,link):
        self.node_tree.set_changes(True)
        to_idname = link.to_socket.bl_idname
        from_idname = link.from_socket.bl_idname
        if from_idname in link.to_socket.connects_to and to_idname in link.from_socket.connects_to:
            if self == link.to_node:
                link.to_socket.update_socket(self,link)
            else:
                link.from_socket.update_socket(self,link)
            self.on_link_insert(link)
        else:
            add_to_remove_links(link)


    ### DRAW NODE
    def draw_node(self,context,layout): pass


    def draw_buttons(self,context,layout):
        self.draw_node(context,layout)


    ### DRAW NODE PANEL
    def draw_node_panel(self,context,layout): pass


    def draw_buttons_ext(self,context,layout):
        self.draw_node_panel(context,layout)
        
        
    ### CREATE SOCKETS
    def add_string_input(self,label,removable=False): return self.add_input("SN_StringSocket",label,removable)
    def add_string_output(self,label,removable=False): return self.add_output("SN_StringSocket",label,removable)
    def add_dynamic_data_input(self,label): return self.add_input("SN_DynamicDataSocket",label,False)
    def add_dynamic_data_output(self,label): return self.add_output("SN_DynamicDataSocket",label,False)
    def add_execute_input(self,label,removable=False): return self.add_input("SN_ExecuteSocket",label,removable)
    def add_execute_output(self,label,removable=False): return self.add_output("SN_ExecuteSocket",label,removable)
    def add_dynamic_execute_input(self,label): return self.add_input("SN_DynamicExecuteSocket",label,False)
    def add_dynamic_execute_output(self,label): return self.add_output("SN_DynamicExecuteSocket",label,False)
    def add_interface_input(self,label,removable=False): return self.add_input("SN_InterfaceSocket",label,removable)
    def add_interface_output(self,label,removable=False): return self.add_output("SN_InterfaceSocket",label,removable)
    def add_dynamic_interface_input(self,label): return self.add_input("SN_DynamicInterfaceSocket",label,False)
    def add_dynamic_interface_output(self,label): return self.add_output("SN_DynamicInterfaceSocket",label,False)
    
    
    def add_input(self,idname,label,removable):
        self.node_tree.set_changes(True)
        socket = self.inputs.new(idname,label)
        socket.setup_socket(removable,label)
        return socket
    
    
    def add_output(self,idname,label,removable):
        self.node_tree.set_changes(True)
        socket = self.outputs.new(idname,label)
        socket.setup_socket(removable,label)
        return socket
    
    
    ### EVALUATE CODE
    
    
    def list_values(self, value_list, indents):
        code = ""
        for value in value_list:
            code += " "*indents*4 + value + "\n"
        if len(code) >= indents*4:
            return code[indents*4:]
        return code
    
    
    def list_blocks(self, block_list, indents):
        return combine_blocks(block_list, indents)


    ### RETURNED CODE
    def code_imports(self,context,main_tree): pass #TODO:optional only once in return vvv
    def code_register(self,context,main_tree): pass
    def code_unregister(self,context,main_tree): pass
    def code_imperative(self,context,main_tree): pass
    def code_evaluate(self,context,main_tree,touched_socket): pass
    
    
    ### RETURNED TYPES
    def what_layout(self,socket): pass
