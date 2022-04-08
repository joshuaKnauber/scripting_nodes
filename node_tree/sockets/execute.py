import bpy
from .base_socket import ScriptingSocket

    
    
class SN_ExecuteSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    bl_idname = "SN_ExecuteSocket"
    output_limit = 1
    socket_shape = "DIAMOND"
    is_program = True
    bl_label = "Execute"
    default_python_value = ""

    def get_color(self, context, node):
        return (1, 1, 1)
    
    def draw_socket(self, context, layout, node, text, minimal=False):
        layout.label(text=text)