import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_IconSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Icon"
    sn_type = "ICON"
    socket_shape = "SQUARE"
    
    allow_value: bpy.props.BoolProperty(default=True)
    is_icon_value: bpy.props.BoolProperty(default=False)
    
    def get_value(self, indents=0):
        if self.is_linked:
            if self.is_output:
                return process_node(self.node, self)
            else:
                value = self.links[0].from_socket.value
                if hasattr(self.links[0].from_socket,"is_icon_value"):
                    if self.links[0].from_socket.is_icon_value and not self.allow_value:
                        return "\"ERROR\""
                return value
        return ""
    
    def icon_line(self):
        value = self.get_value()
        if value:
            if not value.isupper():
                value = f"icon_value={value},"
            else:
                if "'" in value or "\"" in value:
                    value = f"icon={value},"
                else:
                    value = f"icon='{value}',"
        return value

    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def draw_color(self, context, node):
        c = (0.3, 1, 0.3)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)