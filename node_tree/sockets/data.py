import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node



class SN_DataSocket(bpy.types.NodeSocket, ScriptingSocket):

    group = "DATA"
    bl_label = "Data"
    socket_type = "DATA"
        
    def default_value(self):
        return "\"\""

    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def get_color(self, context, node):
        return (0.5,0.5,0.5)
    


class SN_DynamicDataSocket(bpy.types.NodeSocket, ScriptingSocket):

    group = "DATA"
    bl_label = "Data"
    socket_type = "DATA"
    
    dynamic = True
    to_add_idname = "SN_DataSocket"
    
    
    def setup(self):
        self.addable = True