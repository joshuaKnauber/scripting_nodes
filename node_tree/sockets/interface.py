import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_InterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Interface"
    sn_type = "INTERFACE"
    connects_to = ["SN_InterfaceSocket", "SN_DynamicInterfaceSocket"]
    socket_shape = "DIAMOND"
    output_limit = 1

    def get_value(self, indents=0):
        if self.is_linked:
            if self.is_output:
                return self.links[0].to_socket.get_value(indents)
            else:
                return process_node(self.node, self, indents)
        return ""
    
    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def draw_color(self, context, node):
        c = (1, 0.7, 0)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)
    
    

class SN_DynamicInterfaceSocket(bpy.types.NodeSocket, DynamicSocket):
    socket_shape = "DIAMOND"
    connects_to = ["SN_InterfaceSocket"]
    add_idname = "SN_InterfaceSocket"