import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_IconSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Icon"
    sn_type = "ICON"
    socket_shape = "SQUARE"
    
    def get_return_value(self):
        return ""
    
    
    def icon_line(self):
        value = ""
        if self.is_linked and not self.is_output:
            value = process_node(self.links[0].from_node,self.links[0].from_socket,0)
            if '"' in value:
                value = f"icon={value},"
            else:
                value = f"icon_value={value},"
        return value
            

    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def draw_color(self, context, node):
        c = (0.78, 0.78, 0.16)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)