import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "String"
    sn_type = "STRING"
    
    default_value: bpy.props.StringProperty(default="",
                                            update=ScriptingSocket.socket_value_update,
                                            name="Value",
                                            description="Value of this socket")
    
    def default(self, value):
        self.default_value = value

    def get_value(self, indents=0):
        if self.is_output:
            return process_node(self.node, self)
        else:
            if self.is_linked:
                if self.links[0].from_socket.sn_type in ["STRING", "VARIABLE"]:
                    return self.links[0].from_socket.value
                else:
                    return "str(" + self.links[0].from_socket.value + ")"
            return " "*indents*4 + "\""+self.default_value+"\""

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            row.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        c = (0.3, 1, 0.3)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)
    


class SN_DynamicStringSocket(bpy.types.NodeSocket, DynamicSocket):
    add_idname = "SN_StringSocket"