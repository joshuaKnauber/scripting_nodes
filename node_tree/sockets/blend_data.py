import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_BlendDataSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Blend Data"
    sn_type = "BLEND_DATA"
    socket_shape = "SQUARE"
    
    data_type: bpy.props.StringProperty(default="",
                                        update=ScriptingSocket.socket_value_update)
    
    data_path: bpy.props.StringProperty(default="",
                                        update=ScriptingSocket.socket_value_update)

    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def draw_color(self, context, node):
        c = (0,1,0.8)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)
