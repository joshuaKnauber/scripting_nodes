import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node



class SN_IntegerSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    group = "DATA"
    bl_label = "Integer"
    socket_type = "INTEGER"
    
    
    value: bpy.props.IntProperty(default=1,
                                    name="Value",
                                    description="Value of this socket",
                                    update=ScriptingSocket.auto_compile)
    
    value_three: bpy.props.IntVectorProperty(default=(1,1,1),
                                                size=3,
                                                name="Value",
                                                description="Value of this socket",
                                                update=ScriptingSocket.auto_compile)
    
    value_four: bpy.props.IntVectorProperty(default=(1,1,1,1),
                                                size=4,
                                                name="Value",
                                                description="Value of this socket",
                                                update=ScriptingSocket.auto_compile)
    
    
    subtype: bpy.props.EnumProperty(items=[("NONE","None","None"),
                                            ("VECTOR3","Vector 3","Vector 3"),
                                            ("VECTOR4","Vector 4","Vector 4")])
    
    copy_attributes = ["value","value_three","value_four"]
    
    
    def set_default(self, value):
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
            return str((self.value_four[0],self.value_four[1],self.value_four[2],self.value_four[2]))
    
    
    def convert_data(self, code):
        if self.subtype == "NONE":
            return "sn_cast_int(" + code + ")"
        elif self.subtype == "VECTOR3":
            return "sn_cast_int_vector(" + code + ", 3)"
        elif self.subtype == "VECTOR4":
            return "sn_cast_int_vector(" + code + ", 4)"
        
        
    def convert_subtype(self, code):
        return self.convert_data(code)


    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            if not "VECTOR" in self.subtype:
                row.prop(self, "value", text=text)
            else:
                col = row.column(align=True)
                if self.subtype == "VECTOR3":
                    col.prop(self, "value_three", text=text)
                elif self.subtype == "VECTOR4":
                    col.prop(self, "value_four", text=text)
    
    
    def get_color(self, context, node):
        return (0.3, 0.3, 1)
    


class SN_DynamicIntegerSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    group = "DATA"
    bl_label = "Integer"
    socket_type = "INTEGER"
    
    dynamic = True
    to_add_idname = "SN_IntegerSocket"
    
    
    subtype: bpy.props.EnumProperty(items=[("NONE","None","None"),
                                            ("VECTOR3","Vector 3","Vector 3"),
                                            ("VECTOR4","Vector 4","Vector 4")])
    

    
    def setup(self):
        self.addable = True