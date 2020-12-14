import bpy



dynamic_links = []
def get_dynamic_links(): return dynamic_links


remove_links = []
def get_remove_links(): return remove_links
def add_to_remove_links(link): remove_links.append(link)


def get_socket_index(socket):
    return int(socket.path_from_id().split("[")[-1].replace("]",""))



class ScriptingSocket:
    connects_to = []
    socket_shape = "CIRCLE"
    removable: bpy.props.BoolProperty(default=False)
    default_text: bpy.props.StringProperty()
    output_limit = 9999
    input_limit = 1
    
    def setup(self): pass

    def setup_socket(self,removable,label):
        self.display_shape = self.socket_shape
        self.removable = removable
        self.default_text = label
        self.link_limit = 0
        self.setup()
        
    def update(self,node,link): pass
    
    def get_socket_index(self,collection):
        for i, socket in enumerate(collection):
            if socket == self:
                return i
        return 0
        
    def update_socket(self,node,link):
        if self.is_output and len(node.outputs[self.get_socket_index(node.outputs)].links)+1 > self.output_limit:
            add_to_remove_links(link)
        elif not self.is_output and len(node.inputs[self.get_socket_index(node.inputs)].links)+1 > self.input_limit:
            add_to_remove_links(link)
        else:
            self.update(node,link)
        
    def draw_remove_socket(self,layout):
        op = layout.operator("sn.remove_socket", text="",icon="REMOVE", emboss=False)
        op.index = get_socket_index(self)
        op.tree_name = self.node.node_tree.name
        op.node_name = self.node.name
        op.is_output = self.is_output
        
    def draw_socket(self,context,layout,row,node,text): pass
        
    def draw(self, context, layout, node, text):
        row = layout.row(align=True)
        if self.is_output:
            row.alignment = "RIGHT"
        else:
            row.alignment = "LEFT"
        if self.removable and not self.is_output:
            self.draw_remove_socket(row)
        self.draw_socket(context,layout,row,node,text)
        if self.removable and self.is_output:
            self.draw_remove_socket(row)



class SN_RemoveSocket(bpy.types.Operator):
    bl_idname = "sn.remove_socket"
    bl_label = "Remove Socket"
    bl_description = "Removes this socket"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    tree_name: bpy.props.StringProperty()
    node_name: bpy.props.StringProperty()
    is_output: bpy.props.BoolProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        node = bpy.data.node_groups[self.tree_name].nodes[self.node_name]
        if self.is_output:
            node.outputs.remove(node.outputs[self.index])
        else:
            node.inputs.remove(node.inputs[self.index])
        return {"FINISHED"}



class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "String"
    connects_to = ["SN_StringSocket","SN_FloatSocket","SN_IntSocket","SN_DynamicDataSocket"]
    
    default_value: bpy.props.StringProperty(default="",
                                    name="Value",
                                    description="Value of this socket")
    
    @property
    def value(self):
        return self.default_value

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            row.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        c = (1.0, 0.4, 0.216)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)



class SN_DynamicDataSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Dynamic"
    connects_to = ["SN_StringSocket","SN_FloatSocket","SN_IntSocket"]
    
    def get_socket_index(self,collection):
        for i, socket in enumerate(collection):
            if socket == self:
                return i
        return 0
    
    def update_input(self,node,link):
        from_socket = link.from_socket
        pos = self.get_socket_index(node.inputs)
        inp = node.add_input(from_socket.bl_idname,self.default_text,True)
        node.inputs.move(len(node.inputs)-1,pos)
        dynamic_links.append((link, from_socket, node.inputs[pos]))
    
    def update_output(self,node,link):
        to_socket = link.to_socket
        pos = self.get_socket_index(node.outputs)
        out = node.add_output(to_socket.bl_idname,self.default_text,True)
        node.outputs.move(len(node.outputs)-1,pos)
        dynamic_links.append((link, to_socket, node.outputs[pos]))
    
    def update(self,node,link):
        if self == link.to_socket:
            self.update_input(node,link)
        else:
            self.update_output(node,link)

    def draw_socket(self, context, layout, row, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (0,0,0,0)
    
    

class SN_ExecuteSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Execute"
    connects_to = ["SN_ExecuteSocket"]
    socket_shape = "DIAMOND"
    input_limit = 9999
    output_limit = 1
    
    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def draw_color(self, context, node):
        c = (1, 1, 1)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)
    
    

class SN_InterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Interface"
    connects_to = ["SN_InterfaceSocket"]
    socket_shape = "DIAMOND"
    input_limit = 9999
    output_limit = 1
    
    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def draw_color(self, context, node):
        c = (1, 0.7, 0)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)