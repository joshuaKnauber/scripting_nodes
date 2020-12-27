import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_FloatSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Float"
    sn_type = "NUMBER"
        
    default_value: bpy.props.FloatProperty(default=0,
                                            update=ScriptingSocket.socket_value_update,
                                            name="Value",
                                            description="Value of this socket")
    
    array_three_value: bpy.props.FloatVectorProperty(default=(0,0,0),
                                                     size=3,
                                                     update=ScriptingSocket.socket_value_update,
                                                     name="Value",
                                                     description="Value of this socket")
    
    array_four_value: bpy.props.FloatVectorProperty(default=(0,0,0,0),
                                                     size=4,
                                                     update=ScriptingSocket.socket_value_update,
                                                     name="Value",
                                                     description="Value of this socket")
    is_array: bpy.props.BoolProperty(default=False)
    array_size: bpy.props.IntProperty(default=3,min=3,max=4)
    
    def set_default(self, value):
        self.default_value = value
        self.array_three_value = (value,value,value)
        self.array_four_value = (value,value,value,value)
        
    def return_value(self):
        if self.is_array:
            if self.array_size == 3:
                value = self.array_three_value
                return str((value[0],value[1],value[2]))
            value = self.array_four_value
            return str((value[0],value[1],value[2],value[3]))
        return str(self.default_value)
                
    def get_value(self, indents=0):       
        if self.is_output:
            return process_node(self.node, self)
        else:
            if self.is_linked:
                if self.links[0].from_socket.sn_type == "VARIABLE":
                    return self.links[0].from_socket.value
                elif self.links[0].from_socket.sn_type == "NUMBER":
                    value = self.links[0].from_socket.value
                    if value.isnumeric():
                        return str(float(self.links[0].from_socket.value))
                    else:
                        return "float(" + self.links[0].from_socket.value + ")"
                else:
                    value = self.links[0].from_socket.value
                    if value.isnumeric():
                        return "float(" + value + ")"
                    return "float(bool(" + value + "))"
            return " "*indents*4 + self.return_value()

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            if self.is_array:
                col = row.column()
                if self.array_size == 3:
                    col.prop(self, "array_three_value", text=text)
                else:
                    col.prop(self, "array_four_value", text=text)
            else:
                row.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        c = (0.3, 0.7, 1)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)



class SN_IntegerSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Integer"
    sn_type = "NUMBER"

    slider: bpy.props.BoolProperty(default=False)

    default_value: bpy.props.IntProperty(default=0,
                                            update=ScriptingSocket.socket_value_update,
                                            name="Value",
                                            description="Value of this socket")

    def set_default(self, value):
        self.default_value = value

    def get_value(self, indents=0):
        if self.is_output:
            return process_node(self.node, self)
        else:
            if self.is_linked:
                if self.links[0].from_socket.sn_type == "VARIABLE":
                    return self.links[0].from_socket.value
                elif self.links[0].from_socket.sn_type == "NUMBER":
                    value = self.links[0].from_socket.value
                    if value.isnumeric():
                        return str(int(self.links[0].from_socket.value))
                    else:
                        return "int(" + self.links[0].from_socket.value + ")"
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