import bpy
from .base_socket import ScriptingSocket

    
    
class SN_InterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    bl_idname = "SN_InterfaceSocket"
    output_limit = 1
    socket_shape = "DIAMOND"
    is_program = True
    bl_label = "Interface"
    default_python_value = ""

    def get_color(self, context, node):
        return (0.9, 0.6, 0)
    
    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)