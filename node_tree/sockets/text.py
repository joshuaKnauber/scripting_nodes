import bpy
from .base_sockets import ScriptingSocket, DynamicSocket


class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "String"
    sn_type = "STRING"
    connects_to = ["SN_StringSocket","SN_DynamicDataSocket"]
    
    default_value: bpy.props.StringProperty(default="",
                                            update=ScriptingSocket.socket_value_update,
                                            name="Value",
                                            description="Value of this socket")

    def get_value(self, indents=0):
        return " "*indents*4 + self.default_value

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            row.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        c = (1, 0.1, 0.75)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)
    
    
class SN_IconSocket(SN_StringSocket):
    
    def get_value(self, indents=0):
        if self.is_linked:
            value = self.links[0].from_socket.value
            if value.isnumeric():
                return f"icon_value={value},"
            elif value:
                return f"icon=\"{value}\","
        return ""