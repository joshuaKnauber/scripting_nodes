import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_BlendDataSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Blend Data"
    sn_type = "BLEND_DATA"
    socket_shape = "SQUARE"
    
    data_type: bpy.props.StringProperty(default="",
                                        update=ScriptingSocket.socket_value_update,
                                        name="Path",
                                        description="Path of this socket")

    def get_value(self, indents=0):
        if self.is_output:
            return process_node(self.node, self)
        else:
            if self.is_linked:
                return self.links[0].from_socket.get_value(indents)
            return " "*indents*4 + "\""+self.default_value+"\""

    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def draw_color(self, context, node):
        c = (0,1,0.8)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)
