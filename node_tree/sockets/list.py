import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node



class SN_ListSocket(bpy.types.NodeSocket, ScriptingSocket):

    group = "DATA"
    bl_label = "List"
    socket_type = "LIST"

    socket_shape = "SQUARE"

    def default_value(self):
        return "[]"

    def convert_data(self, code):
        return "sn_cast_list(" + code + ")"

    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def get_color(self, context, node):
        return (0.6,0.2,1)



class SN_DynamicListSocket(bpy.types.NodeSocket, ScriptingSocket):

    group = "DATA"
    bl_label = "List"
    socket_type = "LIST"
    
    dynamic = True
    to_add_idname = "SN_ListSocket"
    
    
    def setup(self):
        self.addable = True