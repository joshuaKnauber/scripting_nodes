import bpy


class SN_ScriptingBaseNode:

    bl_width_default = 160
    bl_width_min = 40
    bl_width_max = 5000

    bl_icon = "NONE"
    bl_label = "Node"
    node_color = (1,0,1)


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'


    ### INIT NODE
    def on_create(self,context): pass


    def init(self,context):
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
        self.on_link_insert(link)


    ### DRAW NODE
    def draw_node(self,context,layout): pass


    def draw_buttons(self,context,layout):
        self.draw_node(context,layout)


    ### DRAW NODE PANEL
    def draw_node_panel(self,context,layout): pass


    def draw_buttons_ext(self,context,layout):
        self.draw_node_panel(context,layout)
        
        
    ### CREATE SOCKETS
    def add_string_input(self,label): return self.__add_input("SN_StringSocket",label)
    def add_string_output(self,label): return self.__add_output("SN_StringSocket",label)
    def add_float_input(self,label): return self.__add_input("SN_FloatSocket",label)
    def add_float_output(self,label): return self.__add_output("SN_FloatSocket",label)
    def add_int_input(self,label): return self.__add_input("SN_IntSocket",label)
    def add_int_output(self,label): return self.__add_output("SN_IntSocket",label)
    
    
    def __add_input(self,idname,label):
        socket = self.inputs.new(idname,label)
        socket.setup_socket()
        return socket
    
    
    def __add_output(self,idname,label):
        socket = self.outputs.new(idname,label)
        socket.setup_socket()
        return socket


    ### RETURNED CODE
    def code_register(self,context,node_tree,main_tree,socket_data): pass #TODO:optional only once in return vvv
    def code_unregister(self,context,node_tree,main_tree,socket_data): pass
    def code_imperative(self,context,node_tree,main_tree,socket_data): pass
    def code_evaluate(self,context,node_tree,main_tree,socket_data,touched_socket): pass
    
    
    ### RETURNED TYPES
    def what_layout(self,socket): pass
