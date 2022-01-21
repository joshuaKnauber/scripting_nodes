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
        value = getattr(self, self.subtype_attr)
        if "'" in value and not '"' in value:
            value = f"\"{value}\""
        elif '"' in value and not "'" in value:
            value = f"\'{value}\'"
        else:
            if "'" in value and '"' in value:
                self.string_repr_warning = True
            value = f"\'{value}\'"
        if self.subtype == "NONE":
            return value
        return f"r{value}"
            

    default_value: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)
    
    def update_file_path(self, context):
        self["value_file_path"] = bpy.path.abspath(self.value_file_path)
        self._update_value(context)

    value_file_path: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            subtype="FILE_PATH",
                                            update=update_file_path)
    
    def update_dir_path(self, context):
        self["value_dir_path"] = bpy.path.abspath(self.value_dir_path)
        self._update_value(context)

    value_dir_path: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            subtype="DIR_PATH",
                                            update=update_dir_path)

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