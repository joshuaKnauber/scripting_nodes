import bpy
from .base_socket import ScriptingSocket



class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):

    group = "DATA"
    bl_label = "String"


    default_python_value = "\"\""

    def get_python_repr(self):
        return f"\"{self.default_value}\""

    default_value: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)

    value_file_path: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            subtype="FILE_PATH")

    value_dir_path: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            subtype="DIR_PATH")

    subtypes = ["NONE", "FILE_PATH", "DIR_PATH"]
    subtype_values = {"NONE": "default_value", "FILE_PATH": "value_file_path", "DIR_PATH": "value_dir_path"}
    

    def get_color(self, context, node):
        return (0.44, 0.7, 1)

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, self.subtype_attr, text=text)