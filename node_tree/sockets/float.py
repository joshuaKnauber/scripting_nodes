import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node



class SN_FloatSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    group = "DATA"
    bl_label = "Float"
    socket_type = "FLOAT"
    
    
    value: bpy.props.FloatProperty(default=1,
                                    name="Value",
                                    description="Value of this socket")
    
    value_factor: bpy.props.FloatProperty(default=1, soft_min = 0, soft_max = 1, subtype="FACTOR",
                                            name="Value",
                                            description="Value of this socket")
    
    value_three: bpy.props.FloatVectorProperty(default=(1,1,1),
                                                size=3,
                                                name="Value",
                                                description="Value of this socket")
    
    value_four: bpy.props.FloatVectorProperty(default=(1,1,1,1),
                                                size=4,
                                                name="Value",
                                                description="Value of this socket")
    
    value_color: bpy.props.FloatVectorProperty(default=(0.5,0.5,0.5),
                                                    size=3, min=0, max=1,
                                                    subtype="COLOR",
                                                    name="Value",
                                                    description="Value of this socket")

    value_color_alpha: bpy.props.FloatVectorProperty(default=(0.5,0.5,0.5,1),
                                                    size=4, min=0, max=1,
                                                    subtype="COLOR",
                                                    name="Value",
                                                    description="Value of this socket")
    
    
    subtype: bpy.props.EnumProperty(items=[("NONE","None","None"),
                                            ("FACTOR","Factor","Factor"),
                                            ("COLOR","Color","Color"),
                                            ("COLOR_ALPHA","Color Alpha","Color Alpha"),
                                            ("VECTOR3","Vector 3","Vector 3"),
                                            ("VECTOR4","Vector 4","Vector 4")])
    
    copy_attributes = ["value","value_factor","value_color","value_color_alpha","value_three","value_four"]
    
    
    def set_default(self, value):
        if self.subtype == "NONE":
            self.value = value
        elif self.subtype == "FACTOR":
            self.value_factor = value
        elif self.subtype == "COLOR":
            self.value_color = value
        elif self.subtype == "COLOR_ALPHA":
            self.value_color_alpha = value
        elif self.subtype == "VECTOR3":
            self.value_three = value
        elif self.subtype == "VECTOR4":
            self.value_four = value
    
    
    def default_value(self):
        if self.subtype == "NONE":
            return str(self.value)
        elif self.subtype == "FACTOR":
            return str(self.value_factor)
        elif self.subtype == "COLOR":
            return str((self.value_color[0],self.value_color[1],self.value_color[2]))
        elif self.subtype == "COLOR_ALPHA":
            return str((self.value_color_alpha[0],self.value_color_alpha[1],self.value_color_alpha[2],self.value_color_alpha[2]))
        elif self.subtype == "VECTOR3":
            return str((self.value_three[0],self.value_three[1],self.value_three[2]))
        elif self.subtype == "VECTOR4":
            return str((self.value_four[0],self.value_four[1],self.value_four[2],self.value_four[2]))
    
    
    def convert_data(self, code):
        if self.subtype == "NONE":
            return "sn_cast_float(" + code + ")"
        elif self.subtype == "FACTOR":
            return "sn_cast_float(" + code + ")"
        elif self.subtype == "COLOR":
            return "sn_cast_color(" + code + ", False)"
        elif self.subtype == "COLOR_ALPHA":
            return "sn_cast_color(" + code + ", True)"
        elif self.subtype == "VECTOR3":
            return "sn_cast_float_vector(" + code + ", 3)"
        elif self.subtype == "VECTOR4":
            return "sn_cast_float_vector(" + code + ", 4)"
        
        
    def convert_subtype(self, code):
        return self.convert_data(code)


    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            if not "VECTOR" in self.subtype:
                if self.subtype == "NONE":
                    row.prop(self, "value", text=text)
                elif self.subtype == "FACTOR":
                    row.prop(self, "value_factor", text=text)
                elif self.subtype == "COLOR":
                    row.prop(self, "value_color", text=text)
                elif self.subtype == "COLOR_ALPHA":
                    row.prop(self, "value_color_alpha", text=text)
            else:
                col = row.column(align=True)
                if self.subtype == "VECTOR3":
                    col.prop(self, "value_three", text=text)
                elif self.subtype == "VECTOR4":
                    col.prop(self, "value_four", text=text)
    
    
    def get_color(self, context, node):
        if "COLOR" in self.subtype:
            return (0.78, 0.78, 0.16)
        return (0.3, 0.7, 1)
    


class SN_DynamicFloatSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    group = "DATA"
    bl_label = "Float"
    socket_type = "FLOAT"
    
    dynamic = True
    to_add_idname = "SN_FloatSocket"
    
    subtype: bpy.props.EnumProperty(items=[("NONE","None","None"),
                                            ("FACTOR","Factor","Factor"),
                                            ("COLOR","Color","Color"),
                                            ("COLOR_ALPHA","Color Alpha","Color Alpha"),
                                            ("VECTOR3","Vector 3","Vector 3"),
                                            ("VECTOR4","Vector 4","Vector 4")])
    

    
    def setup(self):
        self.addable = True