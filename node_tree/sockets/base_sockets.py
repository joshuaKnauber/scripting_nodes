import bpy
from ...compiler.compiler import process_node



### THE MAIN SCRIPTING SOCKET

class ScriptingSocket:
    
    ### SOCKET GENERAL

    output_limit = 9999


    ### SOCKET OPTIONS
    
    def update_shape(self,context):
        real_shape = self.socket_shape
        if self.return_var_name or self.show_var_name:
            real_shape += "_DOT"
        if not self.display_shape == real_shape:
            self.display_shape = real_shape
            
            
    def update_var_name(self,context):
        self.node.on_var_name_update(self)
        
    
    def update_text(self,context):
        self.name = self.default_text
    
    
    group = "" # DATA | PROGRAM
    socket_type = "" # Required if group is DATA
    
    socket_shape = "CIRCLE" # CIRCLE | SQUARE | DIAMOND
    
    subtype: bpy.props.EnumProperty(items=[("NONE","None","None")]) # The subtype of this socket
    
    dynamic = False # True if this is a dynamic socket
    copy_socket = False # True if the dynamic socket should copy the connected socket
    

    removable: bpy.props.BoolProperty(default=False) # Shows a remove button on the socket

    addable: bpy.props.BoolProperty(default=False) # Shows an add button on the socket
    to_add_idname = "" # Required if addable or dynamic is true
    
    enabled: bpy.props.BoolProperty(default=True) # Defines if the socket is enabled
    disableable: bpy.props.BoolProperty(default=False) # Socket can be disabled
    
    default_text: bpy.props.StringProperty(update=update_text) # The default text of this socket
    mirror_name: bpy.props.BoolProperty(default=False) # Mirrors the name of the connected socket
    take_name: bpy.props.BoolProperty(default=False) # Takes the name of the first connected socket
    
    variable_name: bpy.props.StringProperty(update=update_var_name) # The name of the variable if is_variable is True
    return_var_name: bpy.props.BoolProperty(default=False,update=update_shape) # Always return the var name instead of running make_code
    show_var_name: bpy.props.BoolProperty(default=False,update=update_shape) # Shows the variable name instead of the draw function
    edit_var_name: bpy.props.BoolProperty(default=False) # Defines if the variable name is shown as editable
    
    # general socket attributes that need to be copied
    copy_props = ["default_text","mirror_name","variable_name","return_var_name",
                  "show_var_name","edit_var_name","subtype"]
    copy_attributes = [] # set this to the attributes that should be copied for each socket
    
    ### SETUP SOCKET
        
    def setup(self): pass


    def setup_socket(self,default_text):
        self.display_shape = self.socket_shape
        self.default_text = default_text
        self.setup()
    
        
    ### UPDATE SOCKET
        
    def update(self,node,link): pass


    def update_take_name(self, link):
        if self.take_name:
            if self.is_output: self.default_text = link.to_socket.default_text
            else: self.default_text = link.from_socket.default_text
            self.take_name = False
    
    def update_socket(self,node,link):
        if self.is_output and len(node.outputs[self.get_socket_index(node.outputs)].links) > self.output_limit:
            try: self.node_tree.links.remove(link)
            except: pass

        elif link.to_socket.group != link.from_socket.group:
            try: self.node_tree.links.remove(link)
            except: pass

        elif link.to_socket.dynamic and link.from_socket.dynamic:
            try: self.node_tree.links.remove(link)
            except: pass

        else:
            self.update_take_name(link)
            self.update_dynamic(node, link)
            self.update(node,link)
    
    
    def auto_compile(self,context):
        self.node.node_tree.set_changes(True)
        
        
    ### DYNAMIC SOCKET

    def update_dynamic_output(self,node,link):
        index = self.get_socket_index(node.outputs)

        if self.copy_socket:
            out = node.add_output(link.to_socket.bl_idname, self.default_text)
        else:
            out = node.add_output(self.to_add_idname, self.default_text)

        out.removable = True
        for attr in self.copy_props + self.copy_attributes:
            setattr(out, attr, getattr(self,attr))

        node.outputs.move(len(node.outputs)-1, index)
        socket = link.to_socket
        node.node_tree.links.remove(link)
        node.node_tree.links.new(socket, out)

        node.on_dynamic_add(out, socket)


    def update_dynamic_input(self,node,link):
        index = self.get_socket_index(node.inputs)

        if self.copy_socket:
            inp = node.add_input(link.from_socket.bl_idname, self.default_text)
        else:
            inp = node.add_input(self.to_add_idname, self.default_text)

        inp.removable = True
        for attr in self.copy_props + self.copy_attributes:
            setattr(inp, attr, getattr(self,attr))

        node.inputs.move(len(node.inputs)-1, index)
        socket = link.from_socket
        node.node_tree.links.remove(link)
        node.node_tree.links.new(inp, socket)

        node.on_dynamic_add(inp, socket)


    def update_dynamic(self,node,link):
        if self.dynamic:
            if self.is_output: self.update_dynamic_output(node,link)
            else: self.update_dynamic_input(node,link)
    
    
    ### DRAW SOCKET
        
    def draw_remove_socket(self,layout):
        op = layout.operator("sn.remove_socket", text="",icon="REMOVE", emboss=False)
        op.index = self.get_socket_index()
        op.tree_name = self.node.node_tree.name
        op.node_name = self.node.name
        op.is_output = self.is_output
        
        
    def draw_add_socket(self,layout):
        op = layout.operator("sn.add_socket", text="",icon="ADD", emboss=False)
        op.index = self.get_socket_index()
        op.tree_name = self.node.node_tree.name
        op.node_name = self.node.name
        op.is_output = self.is_output
        op.idname = self.to_add_idname
        
        
    def draw_disable_socket(self,layout):
        layout.prop(self,"enabled",text="",emboss=False,icon="HIDE_OFF" if self.enabled else "HIDE_ON")
        
        
    def draw_as_input(self,row):
        if self.removable and not self.is_output:
            self.draw_remove_socket(row)
        elif self.addable and not self.is_output:
            self.draw_add_socket(row)
        elif self.disableable and not self.is_output:
            self.draw_disable_socket(row)
        
        
    def draw_as_output(self,row):
        if self.removable and self.is_output:
            self.draw_remove_socket(row)   
        elif self.addable and self.is_output:
            self.draw_add_socket(row)
        elif self.disableable and self.is_output:
            self.draw_disable_socket(row)
    
    
    def draw_variable(self, row):
        if self.edit_var_name:
            row.prop(self,"variable_name",text="")
        else:
            row.label(text=self.variable_name)
            
            
    def get_text(self):
        if self.mirror_name and self.is_linked:
            if self.is_output: return self.links[0].to_socket.default_text
            else: return self.links[0].from_socket.default_text
        return self.default_text
        
        
    def draw_socket(self,context,layout,row,node,text):
        """ overwrite this to draw the sockets property """
        row.label(text=text)


    def draw(self, context, layout, node, text):
        row = layout.row(align=False)
        if self.disableable:
            row.enabled = self.enabled

        if self.is_output:
            row.alignment = "RIGHT"

        self.draw_as_input(row)
        if self.show_var_name and not self.dynamic: self.draw_variable(row)
        else: self.draw_socket(context,layout,row,node,self.get_text())
        self.draw_as_output(row)


    ### SOCKET COLOR


    def get_color(self, context, node):
        """ overwrite this to set the sockets basic color """
        return (0,0,0)


    def draw_color(self, context, node):
        c = self.get_color(context, node)
        if "VECTOR" in self.subtype: c = (0.39, 0.39, 0.78)
        
        if self.is_linked: alpha = 1
        else: alpha = 0.5
        if self.dynamic: alpha = 0
        
        return (c[0], c[1], c[2], alpha)
    
    
    ### UTILITY
        
    
    def get_socket_index(self,collection=None):
        if not collection:
            collection = self.node.inputs
            if self.is_output:
                collection = self.node.outputs
        for i, socket in enumerate(collection):
            if socket == self:
                return i
        return 0
            
            
    ### SOCKET RETURN VALUES
    
    
    def convert_data(self, code):
        """ overwrite this function to return the code with a conversion function for different socket types """
        return code
    
    
    def convert_subtype(self, code):
        """ overwrite this function to return the code with a conversion function for different subtypes """
        return code
    
    
    def default_value(self):
        """ overwrite this function to return the proper socket value for this node """
        return ""
    
    
    def set_default(self, value):
        """ overwrite this function to set the default value of the socket """
        pass
    
    
    def indent_line(self, code, indents):
        if not code: return code
        return " "*indents*4 + code
    
    
    def same_group(self):
        if self.is_output:
            return self.group == self.links[0].to_socket.group
        return self.group == self.links[0].from_socket.group
        
    
    def program_code(self, indents):
        # handle wrongly connected program outputs
        if not self.socket_type == self.links[0].to_socket.socket_type:
            self.node.add_error("Wrong Connection!","These sockets can't be connected",True)
            return self.indent_line(self.default_value(),indents)
        
        # handle correct program outputs
        return process_node(self.links[0].to_node, self.links[0].to_socket, indents)
    
    
    def data_code(self, indents):
        code = process_node(self.links[0].from_node, self.links[0].from_socket)
        
        # handle different data types
        if not self.socket_type == self.links[0].from_socket.socket_type:
            return self.indent_line(self.convert_data( code ),indents)

        # handle different subtypes
        elif not self.subtype == self.links[0].from_socket.subtype:
            return self.indent_line(self.convert_subtype( code ),indents)
        
        # handle the same data types
        return self.indent_line(code,indents)
    
    
    def make_code(self, indents=0):
        # return the variable name of the socket
        if self.return_var_name:
            return self.node.get_python_name(self.variable_name, "variable")

        else:
            # throw an error if the connection is invalid
            if self.is_linked and not self.same_group():
                self.node.add_error("Wrong Connection!","These sockets can't be connected",True)
                return self.indent_line(self.default_value(),indents)
            
            else:
                # handle program sockets (these are guaranteed to be outputs)
                if self.group == "PROGRAM":
                    if self.is_linked:
                        return self.program_code(indents)
                    else:
                        return self.indent_line(self.default_value(),indents)
                
                # handle data sockets (these are guaranteed to be inputs)
                elif self.group == "DATA":
                    if self.is_linked:
                        return self.data_code(indents)
                    return self.indent_line(self.default_value(),indents)
    

    def code(self, indents=0):
        """ call this for getting the sockets code """
        code = self.make_code(indents=indents)
        if "\n" in code: code = code[indents*4:]
        return code
    
    
    def by_attr(self, indents, separator, attr):
        code = ""
        collection = self.node.inputs
        if self.is_output: collection = self.node.outputs
        for socket in collection:
            if getattr(socket, attr) == getattr(self, attr):
                new_code = socket.code(indents)
                code += new_code
                if new_code and not new_code.isspace():
                    code += separator
        if separator and code:
            code = code[:-len(separator)]
        return code
        
        
    def by_name(self, indents=0, separator=""):
        """ return the code for all sockets with this name """
        return self.by_attr(indents,separator,"default_text")
    
    
    def by_type(self, indents=0, separator=""):
        """ return the code for all sockets with this type """
        return self.by_attr(indents,separator,"socket_type")
                


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
            
        node.on_dynamic_remove(self.is_output)
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
            socket = node.add_output(self.idname, add_socket.default_text)
            node.outputs.move(len(node.outputs)-1, self.index)
        else:
            add_socket = node.inputs[self.index]
            socket = node.add_input(self.idname, add_socket.default_text)
            node.inputs.move(len(node.inputs)-1, self.index)
            
        socket.removable = True
        for attr in add_socket.copy_props + add_socket.copy_attributes:
            if hasattr(socket, attr):
                setattr(socket, attr, getattr(add_socket, attr))
                
        node.on_dynamic_add(socket, None)
        return {"FINISHED"}

