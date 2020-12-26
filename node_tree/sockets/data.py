import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_DataSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Data"
    sn_type = "DATA"
    
    default_value: bpy.props.StringProperty(default="",
                                            update=ScriptingSocket.socket_value_update,
                                            name="Value",
                                            description="Value of this socket")

    def get_value(self, indents=0):
        if self.is_output:
            return process_node(self.node, self)
        else:
            if self.is_linked:
                return self.links[0].from_socket.get_value(indents)
            return " "*indents*4 + "\""+self.default_value+"\""

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            row.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        c = (0.5,0.5,0.5)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)
    


class SN_DynamicDataSocket(bpy.types.NodeSocket, DynamicSocket):
    pass