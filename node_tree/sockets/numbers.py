import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_FloatSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Float"
    sn_type = "NUMBER"
    connects_to = ["SN_StringSocket","SN_DynamicDataSocket","SN_BooleanSocket", "SN_FloatSocket", "SN_IntSocket",
                   "SN_VariableSocket","SN_DynamicVariableSocket","SN_DataSocket","SN_DynamicStringSocket"]
    
    slider: bpy.props.BoolProperty(default=False)
    
    default_value: bpy.props.FloatProperty(default=0,
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
                if self.links[0].from_socket.sn_type == "VARIABLE":
                    return self.links[0].from_socket.value
                elif self.links[0].from_socket.sn_type == "NUMBER":
                    return str(float(self.links[0].from_socket.value))
                else:
                    value = self.links[0].from_socket.value
                    if value.isnumeric():
                        return "float(" + value + ")"
                    return "float(bool(" + value + "))"
            return " "*indents*4 + str(self.default_value)

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            row.prop(self, "default_value", text=text, slider=self.slider)

    def draw_color(self, context, node):
        c = (0.3, 0.3, 1)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)



class SN_IntSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Int"
    sn_type = "NUMBER"
    connects_to = ["SN_StringSocket","SN_DynamicDataSocket","SN_BooleanSocket", "SN_FloatSocket", "SN_IntSocket",
                   "SN_VariableSocket","SN_DynamicVariableSocket","SN_DataSocket","SN_DynamicStringSocket"]

    slider: bpy.props.BoolProperty(default=False)

    default_value: bpy.props.IntProperty(default=0,
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
                if self.links[0].from_socket.sn_type == "VARIABLE":
                    return self.links[0].from_socket.value
                elif self.links[0].from_socket.sn_type == "NUMBER":
                    return str(int(self.links[0].from_socket.value))
                else:
                    value = self.links[0].from_socket.value
                    if value.isnumeric():
                        return "int(" + value + ")"
                    return "int(bool(" + value + "))"
            return " "*indents*4 + str(self.default_value)

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            row.prop(self, "default_value", text=text, slider=self.slider)

    def draw_color(self, context, node):
        c = (0.3, 0.3, 1)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)