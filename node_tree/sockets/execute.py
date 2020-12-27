import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_ExecuteSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Execute"
    sn_type = "EXECUTE"
    socket_shape = "DIAMOND"
    output_limit = 1

    # def get_value(self, indents=0):
    #     if self.is_linked:
    #         if self.is_output:
    #             return self.links[0].to_socket.get_value(indents)
    #         else:
    #             return process_node(self.node, self, indents)
    #     return "pass\n"
    
    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def draw_color(self, context, node):
        c = (1, 1, 1)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)
    
    

class SN_DynamicExecuteSocket(bpy.types.NodeSocket, DynamicSocket):
    socket_shape = "DIAMOND"
    add_idname = "SN_ExecuteSocket"