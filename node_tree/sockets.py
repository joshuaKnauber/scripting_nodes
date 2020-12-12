import bpy



class SN_StringSocket(bpy.types.NodeSocket):
    bl_label = "String"
    
    value: bpy.props.StringProperty(default="",
                                    name="Value",
                                    description="Value of this socket")

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)