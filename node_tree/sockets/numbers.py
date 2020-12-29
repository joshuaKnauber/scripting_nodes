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
    
    color_value: bpy.props.FloatVectorProperty(default=(0.5,0.5,0.5),
                                                     size=3,
                                                     subtype="COLOR",
                                                     min=0,
                                                     max=1,
                                                     update=ScriptingSocket.socket_value_update,
                                                     name="Value",
                                                     description="Value of this socket")
    
    color_alpha_value: bpy.props.FloatVectorProperty(default=(0.5,0.5,0.5,1),
                                                     size=4,
                                                     subtype="COLOR",
                                                     min=0,
                                                     max=1,
                                                     update=ScriptingSocket.socket_value_update,
                                                     name="Value",
                                                     description="Value of this socket")
    
    factor_value: bpy.props.FloatProperty(default=0.5,
                                            soft_min=0,
                                            soft_max=1,
                                            update=ScriptingSocket.socket_value_update,
                                            name="Value",
                                            description="Value of this socket")
    
    is_array: bpy.props.BoolProperty(default=False)
    is_color: bpy.props.BoolProperty(default=False)
    use_factor: bpy.props.BoolProperty(default=False)
    array_size: bpy.props.IntProperty(default=3,min=3,max=4)
    
    def set_default(self, value):
        if type(value) == tuple:
            if len(value) == 3:
                self.array_three_value = value
                self.color_value = value
                self.default_value = value[0]
                self.factor_value = value[0]
                self.array_four_value = (value[0],value[1],value[2],value[0])
                self.color_alpha_value = (value[0],value[1],value[2],value[0])
            elif len(value) == 4:
                self.array_four_value = value
                self.color_alpha_value = value
                self.default_value = value[0]
                self.array_three_value = (value[0],value[1],value[2])
                self.color_value = (value[0],value[1],value[2])
        else:
            self.default_value = value
            self.factor_value = value
            self.array_three_value = (value,value,value)
            self.color_value = (value,value,value)
            self.array_four_value = (value,value,value,value)
            self.color_alpha_value = (value,value,value,value)
        
    def get_return_value(self):
        if self.is_array:
            if self.array_size == 3:
                value = self.array_three_value
                if self.is_color:
                    value = self.color_value
                return str((value[0],value[1],value[2]))
            value = self.array_four_value
            if self.is_color:
                value = self.color_alpha_value
            return str((value[0],value[1],value[2],value[3]))
        if self.use_factor:
            return str(self.factor_value)
        return str(self.default_value)
    
    def value_is_number(self,value):
        try:
            float(value)
            return True
        except:
            return False
    
    def value_is_vector(self,value):
        try:
            value = eval(value)
            if type(value) == tuple:
                for el in value:
                    if not type(el) == float and not type(el) == int:
                        return False
                return True
            return False
        except:
            return False
    
    def process_value(self,value):
        real_value = eval(value)
        if type(real_value) == tuple:
            if not self.is_array:
                value = str(real_value[0])
            else:
                if self.array_size != len(real_value):
                    if self.array_size == 3:
                        value = str((real_value[0],real_value[1],real_value[2])) 
                    else:
                        value = str((real_value[0],real_value[1],real_value[2],1))
        else:
            if self.is_array:
                if self.array_size == 3:
                    value = str((real_value,real_value,real_value)) 
                else:
                    value = str((real_value,real_value,real_value,real_value)) 
        return value
    
    def cast_value(self,value):
        value = value.replace('"',"")
        if self.value_is_number(value):
            real_value = float(value)
            if self.is_array:
                if self.array_size == 3:
                    value = str((real_value,real_value,real_value))
                else:
                    value = str((real_value,real_value,real_value,real_value))
        elif self.value_is_vector(value):
            real_value = eval(value)
            if not self.is_array:
                value = str(real_value[0])
            elif len(self.array_size) != len(real_value):
                if self.array_size == 3:
                    value = str((real_value[0],real_value[1],real_value[2]))
                else:
                    value = str((real_value[0],real_value[1],real_value[2],1))
        else:
            value = str(float(bool(value)))
        return value

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            if self.is_array:
                if self.array_size == 3:
                    if self.is_color:
                        row.prop(self, "color_value", text=text)
                    else:
                        col = row.column()
                        col.prop(self, "array_three_value", text=text)
                else:
                    if self.is_color:
                        row.prop(self, "color_alpha_value", text=text)
                    else:
                        col = row.column()
                        col.prop(self, "array_four_value", text=text)
            else:
                if self.use_factor:
                    row.prop(self, "factor_value", text=text, slider=True)
                else:
                    row.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        if self.is_array:
            if self.is_color:
                c = (0.78, 0.78, 0.16)
            else:
                c = (0.39, 0.39, 0.78)
        else:
            c = (0.3, 0.7, 1)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)



class SN_IntegerSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Integer"
    sn_type = "NUMBER"

    default_value: bpy.props.IntProperty(default=0,
                                            update=ScriptingSocket.socket_value_update,
                                            name="Value",
                                            description="Value of this socket")
    
    array_three_value: bpy.props.IntVectorProperty(default=(0,0,0),
                                                     size=3,
                                                     update=ScriptingSocket.socket_value_update,
                                                     name="Value",
                                                     description="Value of this socket")
    
    array_four_value: bpy.props.IntVectorProperty(default=(0,0,0,0),
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
    
    def value_is_vector(self,value):
        try:
            value_value = eval(value)
            if type(value) == tuple:
                for el in value:
                    if not type(el) == float and not type(el) == int:
                        return False
                return True
            return False
        except:
            return False
    
    def process_value(self,value):
        real_value = eval(value)
        if type(real_value) == tuple:
            if not self.is_array:
                value = str(real_value[0])
            else:
                if self.array_size != len(real_value):
                    if self.array_size == 3:
                        value = str((real_value[0],real_value[1],real_value[2])) 
                    else:
                        value = str((real_value[0],real_value[1],real_value[2],1))
        else:
            if self.is_array:
                if self.array_size == 3:
                    value = str((real_value,real_value,real_value)) 
                else:
                    value = str((real_value,real_value,real_value,real_value)) 
        return value
    
    def cast_value(self,value):
        value = value.replace('"',"")
        if self.value_is_number(value):
            real_value = int(float(value))
            if self.is_array:
                if self.array_size == 3:
                    value = str((real_value,real_value,real_value))
                else:
                    value = str((real_value,real_value,real_value,real_value))
        elif self.value_is_vector(value):
            real_value = eval(value)
            if not self.is_array:
                value = str(real_value[0])
            elif len(self.array_size) != len(real_value):
                if self.array_size == 3:
                    value = str((real_value[0],real_value[1],real_value[2]))
                else:
                    value = str((real_value[0],real_value[1],real_value[2],1))
        else:
            value = str(int(bool(value)))
        return value

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
        if self.is_array:
            c = (0.39, 0.39, 0.78)
        else:
            c = (0.3, 0.3, 1)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)