import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_BooleanSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Boolean"
    sn_type = "BOOLEAN"
    
    default_value: bpy.props.BoolProperty(default=True,
                                            update=ScriptingSocket.socket_value_update,
                                            name="Value",
                                            description="Value of this socket")
    
    array_three_value: bpy.props.BoolVectorProperty(default=(True,True,True),
                                                     size=3,
                                                     update=ScriptingSocket.socket_value_update,
                                                     name="Value",
                                                     description="Value of this socket")
    
    array_four_value: bpy.props.BoolVectorProperty(default=(True,True,True,True),
                                                     size=4,
                                                     update=ScriptingSocket.socket_value_update,
                                                     name="Value",
                                                     description="Value of this socket")
    
    is_array: bpy.props.BoolProperty(default=False)
    array_size: bpy.props.IntProperty(default=3,min=3,max=4)
    
    def set_default(self, value):
        if type(value) == tuple:
            if len(value) == 3:
                self.array_three_value = value
                self.default_value = value[0]
                self.array_four_value = (value[0],value[1],value[2],value[0])
            elif len(value) == 4:
                self.array_four_value = value
                self.default_value = value[0]
                self.array_three_value = (value[0],value[1],value[2])
        else:
            self.default_value = value
            self.array_three_value = (value,value,value)
            self.array_four_value = (value,value,value,value)
        
    def get_return_value(self):
        if self.is_array:
            if self.array_size == 3:
                value = self.array_three_value
                return str((value[0],value[1],value[2]))
            value = self.array_four_value
            return str((value[0],value[1],value[2],value[3]))
        return str(self.default_value)
    
    def value_is_number(self,value):
        try:
            float(value)
            return True
        except:
            return False
    
    def value_is_vector(self,value,types=[bool]):
        try:
            value = eval(value)
            if type(value) == tuple:
                for el in value:
                    if not type(el) in types:
                        return False
                return True
            return False
        except:
            return False
    
    def process_value(self,value):
        real_value = eval(value)
        if self.value_is_vector(value):
            if not self.is_array:
                value = str(real_value[0])
            elif self.array_size != len(real_value):
                if self.array_size == 3:
                    value = str((real_value[0],real_value[1],real_value[2]))
                else:
                    value = str((real_value[0],real_value[1],real_value[2],True))
        elif self.is_array:
            if self.array_size == 3:
                value = str((real_value,real_value,real_value))
            else:
                value = str((real_value,real_value,real_value,real_value))
        return value
    
    def cast_value(self,value):
        if not value in ["True","False"]:
            if value == '""':
                value = "False"
            elif self.value_is_number(value.replace('"',"")):
                value = bool(float(value.replace('"',"")))
            elif self.value_is_vector(value,[int,float]):
                value = bool(eval(value)[0])
            else:
                value = str(bool(value))
        if self.is_array:
            if self.array_size == 3:
                value = str((bool(value),bool(value),bool(value)))
            else:
                value = str((bool(value),bool(value),bool(value),bool(value)))
        return value

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            if self.is_array:
                col = row.column(align=True)
                if self.array_size == 3:
                    for i in range(3):
                        col.prop(self, "array_three_value", text=str(self.array_three_value[i]),toggle=True, index=i)
                else:
                    for i in range(4):
                        col.prop(self, "array_four_value", text=str(self.array_four_value[i]),toggle=True, index=i)
            else:
                row.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        if self.is_array:
            c = (0.39, 0.39, 0.78)
        else:
            c = (1, 0.1, 0.1)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)