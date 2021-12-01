import bpy
from .base_socket import ScriptingSocket



class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_StringSocket"
    group = "DATA"
    bl_label = "String"


    default_python_value = "\'\'"
    default_prop_value = ""

    string_repr_warning: bpy.props.BoolProperty(default=False,
                                                name="Potential Error Warning!",
                                                description="You're using two types of quotes in your string! Be aware that this will cause syntax errors if you don't change ' to \\'")

    def get_python_repr(self):
        self.string_repr_warning = False
        value = self.default_value
        if "'" in value and not '"' in value:
            return f"\"{value}\""
        elif '"' in value and not "'" in value:
            return f"\'{value}\'"
        else:
            if "'" in value and '"' in value:
                self.string_repr_warning = True
            return f"\'{value}\'"
            

    default_value: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)

    value_file_path: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            subtype="FILE_PATH",
                                            update=ScriptingSocket._update_value)

    value_dir_path: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            subtype="DIR_PATH",
                                            update=ScriptingSocket._update_value)

    subtypes = ["NONE", "FILE_PATH", "DIR_PATH"]
    subtype_values = {"NONE": "default_value", "FILE_PATH": "value_file_path", "DIR_PATH": "value_dir_path"}
    

    def get_color(self, context, node):
        return (0.44, 0.7, 1)

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            if self.string_repr_warning:
                layout.prop(self, "string_repr_warning", text="", icon="ERROR", emboss=False)
            layout.prop(self, self.subtype_attr, text=text)