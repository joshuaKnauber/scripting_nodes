import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node



class SN_IconSocket(bpy.types.NodeSocket, ScriptingSocket):

    group = "DATA"
    bl_label = "Icon"
    socket_type = "ICON"
    
    socket_shape = "SQUARE"
    
    def default_value(self):
        return "0"
    

    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)


    def get_color(self, context, node):
        return (0.78, 0.78, 0.16)