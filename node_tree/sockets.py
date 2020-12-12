import bpy



class ScriptingSocket:
    connects_to = []
    socket_shape = "CIRCLE"
    
    def setup(self): pass

    def setup_socket(self):
        self.display_shape = self.socket_shape
        self.setup()



class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "String"
    connects_to = ["SN_StringSocket","SN_FloatSocket","SN_IntSocket"]
    socket_shape = "DIAMOND"
    
    text: bpy.props.StringProperty(default="",
                                    name="Value",
                                    description="Value of this socket")
    
    @property
    def value(self):
        return self.text

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "text", text=text)

    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)



class SN_FloatSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Float"
    connects_to = ["SN_StringSocket","SN_FloatSocket","SN_IntSocket"]
    
    number: bpy.props.FloatProperty(default=0.0,
                                    name="Value",
                                    description="Value of this socket")
    
    @property
    def value(self):
        return self.number

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "number", text=text)

    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)



class SN_IntSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Integer"
    connects_to = ["SN_StringSocket","SN_FloatSocket","SN_IntSocket"]
    
    number: bpy.props.IntProperty(default=0,
                                    name="Value",
                                    description="Value of this socket")
    
    @property
    def value(self):
        return self.number

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "number", text=text)

    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)