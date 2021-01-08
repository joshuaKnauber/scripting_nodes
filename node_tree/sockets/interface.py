import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node



class SN_InterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    group = "PROGRAM"
    bl_label = "Interface"
    socket_type = "INTERFACE"

    socket_shape = "DIAMOND"
    
    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def get_color(self, context, node):
        return (1, 0.7, 0)
    
    

class SN_DynamicInterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    group = "PROGRAM"
    bl_label = "Interface"
    socket_type = "INTERFACE"

    socket_shape = "DIAMOND"
    
    dynamic = True
    to_add_idname = "SN_InterfaceSocket"
    
    def setup(self):
        self.addable = True