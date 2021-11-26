import bpy
from .base_sockets import ScriptingSocket

    
    
class SN_ExecuteSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    output_limit = 1
    socket_shape = "DIAMOND"
    is_program = True
    bl_label = "Execute"

    def get_color(self, context, node):
        return (1, 1, 1)
    
    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)