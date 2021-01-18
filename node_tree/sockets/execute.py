import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node

    
    
class SN_ExecuteSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    group = "PROGRAM"
    bl_label = "Execute"
    socket_type = "EXECUTE"
    output_limit = 1

    socket_shape = "DIAMOND"
    
    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def get_color(self, context, node):
        return (1, 1, 1)
    


class SN_DynamicExecuteSocket(bpy.types.NodeSocket, ScriptingSocket):
    group = "PROGRAM"
    bl_label = "Execute"
    socket_type = "EXECUTE"

    socket_shape = "DIAMOND"
    
    dynamic = True
    to_add_idname = "SN_ExecuteSocket"
    
    def setup(self):
        self.addable = True