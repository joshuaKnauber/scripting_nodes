import bpy
from .base_sockets import ScriptingSocket, DynamicSocket


class SN_InterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Interface"
    sn_type = "INTERFACE"
    connects_to = ["SN_InterfaceSocket", "SN_DynamicInterfaceSocket"]
    socket_shape = "DIAMOND"
    output_limit = 1

    def get_value(self, indents=0):
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