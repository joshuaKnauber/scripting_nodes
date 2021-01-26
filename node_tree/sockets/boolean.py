import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node



class SN_BooleanSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    group = "DATA"
    bl_label = "Boolean"
    socket_type = "BOOLEAN"
    
    
    value: bpy.props.BoolProperty(default=True,
                                            name="Value",
                                            description="Value of this socket",
                                            update=ScriptingSocket.auto_compile)
    
    value_three: bpy.props.BoolVectorProperty(default=(True,True,True),
                                                     size=3,
                                                     name="Value",
                                                     description="Value of this socket",
                                                     update=ScriptingSocket.auto_compile)
    
    value_four: bpy.props.BoolVectorProperty(default=(True,True,True,True),
                                                     size=4,
                                                     name="Value",
                                                     description="Value of this socket",
                                                     update=ScriptingSocket.auto_compile)
    
    
    subtype: bpy.props.EnumProperty(items=[("NONE","None","None"),
                                            ("VECTOR3","Vector 3","Vector 3"),
                                            ("VECTOR4","Vector 4","Vector 4")])
    
    copy_attributes = ["value","value_three","value_four"]
    
    
    def set_default(self,value):
        if self.subtype == "NONE":
            self.value = value
        elif self.subtype == "VECTOR3":
            self.value_three = value
        elif self.subtype == "VECTOR4":
            self.value_four = value
    
    
    def default_value(self):
        if self.subtype == "NONE":
            return str(self.value)
        elif self.subtype == "VECTOR3":
            return str((self.value_three[0],self.value_three[1],self.value_three[2]))
        elif self.subtype == "VECTOR4":
            return str((self.value_four[0],self.value_four[1],self.value_four[2],self.value_four[3]))
    
    
    def convert_data(self, code):
        if self.subtype == "NONE":
            return "sn_cast_boolean(" + code + ")"
        elif self.subtype == "VECTOR3":
            return "sn_cast_boolean_vector(" + code + ", 3)"
        elif self.subtype == "VECTOR4":
            return "sn_cast_boolean_vector(" + code + ", 4)"
        
        
    def convert_subtype(self, code):
        return self.convert_data(code)


    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            if self.subtype == "NONE":
                row.prop(self, "value", text=text)
            else:
                col = row.column(align=True)
                if self.subtype == "VECTOR3":
                    for i in range(3): col.prop(self, "value_three", text=str(self.value_three[i]), index=i, toggle=True)
                elif self.subtype == "VECTOR4":
                    for i in range(4): col.prop(self, "value_four", text=str(self.value_four[i]), index=i, toggle=True)
    
    
    def get_color(self, context, node):
        return (1, 0.1, 0.1)
    


class SN_DynamicBooleanSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    group = "DATA"
    bl_label = "Boolean"
    socket_type = "BOOLEAN"
    
    dynamic = True
    to_add_idname = "SN_BooleanSocket"
    
    subtype: bpy.props.EnumProperty(items=[("NONE","None","None"),
                                            ("VECTOR3","Vector 3","Vector 3"),
                                            ("VECTOR4","Vector 4","Vector 4")])
    

    
    def setup(self):
        self.addable = True