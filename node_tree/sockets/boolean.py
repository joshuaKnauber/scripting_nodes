import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_BooleanSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Boolean"
    sn_type = "BOOLEAN"
    connects_to = ["SN_StringSocket","SN_DynamicDataSocket","SN_BooleanSocket","SN_FloatSocket", "SN_IntSocket",
                   "SN_VariableSocket","SN_DynamicVariableSocket"]
    
    default_value: bpy.props.BoolProperty(default=True,
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
                if self.links[0].from_socket.sn_type == "BOOLEAN":
                    return self.links[0].from_socket.value
                else:
                    return "bool(" + self.links[0].from_socket.value + ")"
            return " "*indents*4 + str(self.default_value)

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            row.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        c = (1, 0.1, 0.1)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)