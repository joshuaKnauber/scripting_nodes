import bpy



class SN_RerouteSocket(bpy.types.NodeSocket):

    bl_idname = "SN_RerouteSocket"
    bl_label = "Reroute"

    def draw_color(self, context, node):
        if self.is_output:
            return node.inputs[0].draw_color(context, node)
        if self.is_linked:
            return self.links[0].from_socket.draw_color(context, self.links[0].from_node)
        return (0.3, 0.3, 0.3, 1)
        
    def draw(self, context, layout, node, text):
        layout.label(text=text)