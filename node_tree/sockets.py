import bpy



class ScriptingSocket:
    pass



class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "String"
    
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