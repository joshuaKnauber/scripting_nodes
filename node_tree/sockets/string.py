import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node



class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):

    group = "DATA"
    bl_label = "String"
    socket_type = "STRING"
    
    
    enum_values: bpy.props.StringProperty()
    
    def enum_items(self,context):
        items = []
        if self.enum_values:
            items = eval(self.enum_values)
        if not items:
            items = [("NONE","None","No items have been found for this property")]
        return items


    def update_string(self, context):
        if self.value[-1] == "\\":
            self["value"] = self.value[:-1] + "/"

    def make_absolute(self,context):
        if not self.value_directory == bpy.path.abspath(self.value_directory):
            self.value_directory = bpy.path.abspath(self.value_directory)
        if not self.value_file == bpy.path.abspath(self.value_file):
            self.value_file = bpy.path.abspath(self.value_file)

        if self.value_directory[-1] == "\\":
            self["value_directory"] = self.value_directory[:-1] + "/"
        if self.value_file[-1] == "\\":
            self["value_file"] = self.value_file[:-1] + "/"


    value: bpy.props.StringProperty(name="Value",
                                    description="Value of this socket",
                                    update=update_string)

    value_file: bpy.props.StringProperty(name="Value",
                                        description="Value of this socket",
                                        subtype="FILE_PATH",
                                        update=make_absolute)

    value_directory: bpy.props.StringProperty(name="Value",
                                        description="Value of this socket",
                                        subtype="DIR_PATH",
                                        update=make_absolute)

    value_enum: bpy.props.EnumProperty(name="Value",
                                        description="Value of this socket",
                                        items=enum_items)
    
    
    subtype: bpy.props.EnumProperty(items=[("NONE","None","None"),
                                            ("FILE","File","File"),
                                            ("DIRECTORY","Directory","Directory"),
                                            ("ENUM","Enum","Enum")])
    
    copy_attributes = ["value","value_file","value_directory","value_enum"]
    
    
    def set_default(self,value):
        if self.subtype == "NONE":
            self.value = value
        elif self.subtype == "FILE":
            self.value_file = value
        elif self.subtype == "DIRECTORY":
            self.value_directory = value
        elif self.subtype == "ENUM":
            self.value_enum = value
    
    
    def default_value(self):
        if self.subtype == "NONE":
            return "\"" + self.value + "\""
        elif self.subtype == "FILE":
            return "\"" + self.value_file + "\""
        elif self.subtype == "DIRECTORY":
            return "\"" + self.value_directory + "\""
        elif self.subtype == "ENUM":
            return "\"" + self.value_enum + "\""
    
    
    def convert_data(self, code):
        return "sn_cast_string(" + code + ")"


    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            if self.subtype == "NONE":
                row.prop(self, "value", text=text)
            elif self.subtype == "FILE":
                row.prop(self, "value_file", text=text)
            elif self.subtype == "DIRECTORY":
                row.prop(self, "value_directory", text=text)
            elif self.subtype == "ENUM":
                row.prop(self, "value_enum", text=text)


    def get_color(self, context, node):
        return (0.3, 1, 0.3)
    


class SN_DynamicStringSocket(bpy.types.NodeSocket, ScriptingSocket):
    group = "DATA"
    bl_label = "String"
    socket_type = "STRING"
    
    dynamic = True
    to_add_idname = "SN_StringSocket"
    
    subtype: bpy.props.EnumProperty(items=[("NONE","None","None"),
                                            ("FILE","File","File"),
                                            ("DIRECTORY","Directory","Directory"),
                                            ("ENUM","Enum","Enum")])
    
    
    def setup(self):
        self.addable = True