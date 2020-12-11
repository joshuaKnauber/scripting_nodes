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
