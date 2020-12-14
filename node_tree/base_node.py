import bpy
from .sockets import add_to_remove_links



class SN_ScriptingBaseNode:

    bl_width_default = 160
    bl_width_min = 40
    bl_width_max = 5000

    bl_icon = "NONE"
    bl_label = "Node"
    node_color = (1,0,1)
    
    node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'


    ### INIT NODE
    def on_create(self,context): pass


    def init(self,context):
        self.node_tree = self.id_data
        self.color = self.node_color
        self.use_custom_color = True
        self.on_create(context)


    ### COPY NODE
    def on_copy(self,node): pass


    def copy(self,node):
        self.on_copy(node)


    ### FREE NODE
    def on_free(self): pass


    def free(self):
        self.on_free()


    ### NODE UPDATE
    def on_node_update(self): pass


    def update(self):
        self.on_node_update()


    ### SOCKET UPDATE
    def on_socket_update(self): pass


    def socket_value_update(self, context):
        self.on_socket_update()


    ### LINK UPDATE
    def on_link_insert(self,link): pass


    def insert_link(self,link):
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
    def add_interface_input(self,label,removable=False): return self.add_input("SN_InterfaceSocket",label,removable)
    def add_interface_output(self,label,removable=False): return self.add_output("SN_InterfaceSocket",label,removable)
    
    
    def add_input(self,idname,label,removable):
        socket = self.inputs.new(idname,label)
        socket.setup_socket(removable,label)
        return socket
    
    
    def add_output(self,idname,label,removable):
        socket = self.outputs.new(idname,label)
        socket.setup_socket(removable,label)
        return socket


    ### RETURNED CODE
    def code_register(self,context,node_tree,main_tree,socket_data): pass #TODO:optional only once in return vvv
    def code_unregister(self,context,node_tree,main_tree,socket_data): pass
    def code_imperative(self,context,node_tree,main_tree,socket_data): pass
    def code_evaluate(self,context,node_tree,main_tree,socket_data,touched_socket): pass
    
    
    ### RETURNED TYPES
    def what_layout(self,socket): pass
