import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_DataSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Data"
    sn_type = "DATA"
        
    def get_return_value(self):
        return "\"\""

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)

    def draw_color(self, context, node):
        c = (0.5,0.5,0.5)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)
    


class SN_DynamicDataSocket(bpy.types.NodeSocket, DynamicSocket):
    add_idname = "SN_DataSocket"