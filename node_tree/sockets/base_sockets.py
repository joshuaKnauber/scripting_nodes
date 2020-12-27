import bpy
from ...compiler.compiler import process_node


### PROCESS LINKS THAT NEED TO BE HANDLED DYNAMIC

dynamic_links = []
def get_dynamic_links(): return dynamic_links


### PROCESS LINKS THAT NEED TO BE REMOVED

remove_links = []
def get_remove_links(): return remove_links
def add_to_remove_links(link): remove_links.append(link)


### SOCKET INDEX BY PATH

def get_socket_index(socket):
    return int(socket.path_from_id().split("[")[-1].replace("]",""))


### HANDLE POSSIBLE SOCKET CONNECTIONS

SOCKET_CONNECTIONS = {
    "SHORT": {
        "SN_ExecuteSocket":             "E",
        "SN_DynamicExecuteSocket":      "DE",

        "SN_InterfaceSocket":           "I",
        "SN_DynamicInterfaceSocket":    "DI",

        "SN_BlendDataSocket":           "BD",    
        
        "SN_DataSocket":                "D",
        "SN_DynamicDataSocket":         "DD",
                
        "SN_IntegerSocket":             "IN",
        "SN_FloatSocket":               "FN",  
        
        "SN_BooleanSocket":             "B",
        
        "SN_StringSocket":              "S",
        "SN_DynamicStringSocket":       "DS",
        "SN_IconSocket":                "IC",
        
        "SN_DynamicVariableSocket":     "DV"
    },
    
    "VALUES": {"COLUMNS":   ["E","DE","I","DI","BD","D","DD","IN","FN","B","S","DS","IC","DV"],
                     "E":   [ 1,  1,   0,  0,   0,   0,   0,   0,   0,  0,  0,   0,   0,   0 ],
                    "DE":   [ 1,  0,   0,  0,   0,   0,   0,   0,   0,  0,  0,   0,   0,   0 ],
                     "I":   [ 0,  0,   1,  1,   0,   0,   0,   0,   0,  0,  0,   0,   0,   0 ],
                    "DI":   [ 0,  0,   1,  0,   0,   0,   0,   0,   0,  0,  0,   0,   0,   0 ],
                    "BD":   [ 0,  0,   0,  0,   1,   0,   0,   0,   0,  0,  0,   0,   0,   1 ],
                     "D":   [ 0,  0,   0,  0,   0,   1,   1,   1,   1,  1,  1,   1,   0,   1 ],
                    "DD":   [ 0,  0,   0,  0,   0,   1,   0,   1,   1,  1,  1,   0,   0,   0 ],
                    "IN":   [ 0,  0,   0,  0,   0,   1,   1,   1,   1,  1,  1,   1,   0,   1 ],
                    "FN":   [ 0,  0,   0,  0,   0,   1,   1,   1,   1,  1,  1,   1,   0,   1 ],
                     "B":   [ 0,  0,   0,  0,   0,   1,   1,   1,   1,  1,  1,   1,   0,   1 ],
                     "S":   [ 0,  0,   0,  0,   0,   1,   1,   1,   1,  1,  1,   1,   0,   1 ],
                    "DS":   [ 0,  0,   0,  0,   0,   1,   0,   1,   1,  1,  1,   0,   0,   0 ],
                    "IC":   [ 0,  0,   0,  0,   0,   0,   0,   0,   0,  0,  0,   0,   1,   0 ],
                    "DV":   [ 0,  0,   0,  0,   1,   1,   0,   1,   1,  1,  1,   0,   0,   0 ],}
    
}

def can_connect(idname1,idname2):
    id1 = SOCKET_CONNECTIONS["SHORT"][idname1]
    id2 = SOCKET_CONNECTIONS["SHORT"][idname2]
    col = SOCKET_CONNECTIONS["VALUES"]["COLUMNS"].index(id2)
    return bool(SOCKET_CONNECTIONS["VALUES"][id1][col])


### THE MAIN SCRIPTING SOCKET

class ScriptingSocket:
    
    ### SOCKET TYPE

    sn_type = ""
    output_limit = 9999
    dynamic_overwrite = ""


    ### SOCKET APPEARANCE
    
    socket_shape = "CIRCLE"
    removable: bpy.props.BoolProperty(default=False)
    addable: bpy.props.BoolProperty(default=False)
    
    
    ### ARRAYS
    
    is_array: bpy.props.BoolProperty(default=False)
    array_size: bpy.props.IntProperty(default=3,min=3,max=4)
    
    
    ### SETUP SOCKET
        
    def setup(self): pass


    def setup_socket(self,removable,label):
        self.display_shape = self.socket_shape
        self.removable = removable
        self.default_text = label
        self.setup()
        
    
    def get_socket_index(self,collection):
        for i, socket in enumerate(collection):
            if socket == self:
                return i
        return 0
    
        
    ### UPDATE SOCKET
    
    def update(self,node,link): pass

    
    def update_socket(self,node,link):
        if self.is_output and len(node.outputs[self.get_socket_index(node.outputs)].links)+1 > self.output_limit:
            add_to_remove_links(link)
        else:
            if self.take_name and not self.taken_name:
                if self.is_output:
                    self.taken_name = link.to_socket.name
                else:
                    self.taken_name = link.from_socket.name
            self.update(node,link)
    
    
    def socket_value_update(self,context):
        self.node.node_tree.set_changes(True)
    
    
    ### SOCKET TEXT

    default_text: bpy.props.StringProperty()
    take_name: bpy.props.BoolProperty(default=False)
    taken_name: bpy.props.StringProperty(default="")
    copy_name: bpy.props.BoolProperty(default=False)
        
        
    def get_text(self,text):
        if self.taken_name:
            return self.taken_name
        elif self.is_linked and self.copy_name:
            if self.is_output and not self.links[0].to_socket.copy_name:
                return self.links[0].to_socket.get_text(self.links[0].to_socket.name)
            elif self.is_output and self.links[0].to_socket.copy_name:
                return self.links[0].to_socket.name
            elif not self.is_output and not self.links[0].from_socket.copy_name:
                return self.links[0].from_socket.get_text(self.links[0].from_socket.name)
            elif not self.is_output and self.links[0].from_socket.copy_name:
                return self.links[0].from_socket.name
        return text
    
    
    ### HANDLE VARIABLE SOCKETS
    
    def update_var_name(self,context):
        if not self.var_name:
            self["var_name"] = "Parameter"
        names = []
        if self.is_output:
            for out in self.node.outputs:
                names.append(out.var_name)
        else:
            for inp in self.node.inputs:
                names.append(inp.var_name)
        unique_name = self.node.get_unique_name(self.var_name, names, " ")
        if not self.var_name == unique_name:
            self.var_name = unique_name
        self.node.update_needs_compile(context)


    def update_is_variable(self,context):
        if self.is_variable:
            self.display_shape = self.socket_shape + "_DOT"
        else:
            self.display_shape = self.socket_shape.replace("_DOT","")
        self.node.update_needs_compile(context)


    is_variable: bpy.props.BoolProperty(default=False, update=update_is_variable)
    var_name: bpy.props.StringProperty(default="", update=update_var_name)
    
    
    ### DRAW SOCKET
        
    def draw_remove_socket(self,layout):
        op = layout.operator("sn.remove_socket", text="",icon="REMOVE", emboss=False)
        op.index = get_socket_index(self)
        op.tree_name = self.node.node_tree.name
        op.node_name = self.node.name
        op.is_output = self.is_output
        
        
    def draw_add_socket(self,layout):
        if self.add_idname:
            op = layout.operator("sn.add_socket", text="",icon="ADD", emboss=False)
            op.index = get_socket_index(self)
            op.tree_name = self.node.node_tree.name
            op.node_name = self.node.name
            op.is_output = self.is_output
            op.idname = self.add_idname
        
        
    def draw_socket(self,context,layout,row,node,text):
        """ overwrite this to draw the socket """
        pass
        
        
    def draw(self, context, layout, node, text):
        row = layout.row(align=True)
        if self.is_output:
            row.alignment = "RIGHT"
        else:
            row.alignment = "LEFT"
        if self.removable and not self.is_output:
            self.draw_remove_socket(row)
        elif self.addable and not self.is_output:
            self.draw_add_socket(row)
        if self.is_variable:
            row.prop(self,"var_name",text="")
        else:
            self.draw_socket(context,layout,row,node,self.get_text(text))
        if self.removable and self.is_output:
            self.draw_remove_socket(row)   
        elif self.addable and self.is_output:
            self.draw_add_socket(row)
            

    def draw_color(self, context, node):
        """ overwrite this to draw the socket color """
        return (0,0,0,0)
            
            
    ### SOCKET RETURN VALUES
    
    def make_code(self,indents=0):
        # handle variable sockets
        if self.is_variable:
            return self.node.get_python_name(self.var_name,"parameter")
        
        # handle program sockets
        if self.sn_type in ["EXECUTE","INTERFACE"]:
            if self.is_output:
                if self.is_linked:
                    return self.links[0].to_socket.make_code(indents)
                else:
                    return "pass\n"
            else:
                return process_node(self.node, self, indents)
        
        # handle any data socket
        if self.is_output:
            return process_node(self.node, self, indents)
            
        else:
            if self.is_linked:
                value = self.links[0].from_socket.make_code(indents=indents)
                if self.links[0].from_socket.is_variable:
                    return value
            else:
                value = self.get_return_value()
            
            value = self.process_value(value)
            
            # value = " "*indents*4 + value
            
            return value

    def get_return_value(self):
        """ overwrite this to get the correct return value of the socket as a string """
        return ""

    def set_default(self, value):
        """ overwrite this to set the default value of the socket """
        pass
    
    def process_value(self, value):
        """ overwrite this to modify the value to match the socket type """
        return value
    
    @property
    def value(self):
        """ call this for getting inline code """
        return self.make_code(indents=0)

    def block(self, indents):
        """ call this for getting a block of code """
        code = self.make_code(indents=indents)
        return code[indents*4:]
    
    
    
### DYNAMIC SOCKET BASE        
            
class DynamicSocket(ScriptingSocket):
    bl_label = "Dynamic"
    make_variable = False
    addable: bpy.props.BoolProperty(default=True)
    add_idname = ""
    
    def get_socket_index(self,collection):
        for i, socket in enumerate(collection):
            if socket == self:
                return i
        return 0
    
    def update_input(self,node,link):
        from_socket = link.from_socket
        pos = self.get_socket_index(node.inputs)
        inp = node.add_input(from_socket.bl_idname,self.default_text,True)
        inp.is_variable = self.make_variable
        inp.var_name = link.from_socket.default_text
        inp.copy_name = self.copy_name
        inp.taken_name = self.taken_name
        inp.take_name = self.take_name
        self.taken_name = ""
        node.inputs.move(len(node.inputs)-1,pos)
        dynamic_links.append((link, from_socket, node.inputs[pos]))
    
    def update_output(self,node,link):
        to_socket = link.to_socket
        pos = self.get_socket_index(node.outputs)
        out = node.add_output(to_socket.bl_idname,self.default_text,True)
        out.is_variable = self.make_variable
        out.var_name = link.to_socket.default_text
        out.copy_name = self.copy_name
        out.taken_name = self.taken_name
        out.take_name = self.take_name
        self.taken_name = ""
        node.outputs.move(len(node.outputs)-1,pos)
        dynamic_links.append((link, to_socket, node.outputs[pos]))
    
    def update(self,node,link):
        if self == link.to_socket:
            self.update_input(node,link)
        else:
            self.update_output(node,link)

    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def draw_color(self, context, node):
        return (0,0,0,0)




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
    
    



class SN_AddSocket(bpy.types.Operator):
    bl_idname = "sn.add_socket"
    bl_label = "Add Socket"
    bl_description = "Adds this sockets default type"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    tree_name: bpy.props.StringProperty()
    node_name: bpy.props.StringProperty()
    is_output: bpy.props.BoolProperty()
    index: bpy.props.IntProperty()
    idname: bpy.props.StringProperty()

    def execute(self, context):
        node = bpy.data.node_groups[self.tree_name].nodes[self.node_name]
        if self.is_output:
            add_socket = node.outputs[self.index]
            socket = node.add_output(self.idname,add_socket.default_text,True)
            node.outputs.move(len(node.outputs)-1,self.index)
        else:
            add_socket = node.inputs[self.index]
            socket = node.add_input(self.idname,add_socket.default_text,True)
            node.inputs.move(len(node.inputs)-1,self.index)

        socket.is_variable = add_socket.make_variable
        socket.var_name = add_socket.default_text
        socket.copy_name = add_socket.copy_name
        socket.taken_name = add_socket.taken_name
        socket.take_name = add_socket.take_name
        return {"FINISHED"}

