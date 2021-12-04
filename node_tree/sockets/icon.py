import bpy
from .base_socket import ScriptingSocket



class SN_IconSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_IconSocket"
    group = "DATA"
    bl_label = "Icon"


    default_python_value = "0"
    default_prop_value = 0

    def get_python_repr(self):
        value = self.default_value
        if "'" in value and not '"' in value:
            return f"\"{value}\""
        elif '"' in value and not "'" in value:
            return f"\'{value}\'"
        else:
            if "'" in value and '"' in value:
                self.string_repr_warning = True
            return f"\'{value}\'"
            

    default_value: bpy.props.IntProperty(name="Value",
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)

    named_icon: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            subtype="FILE_PATH",
                                            update=ScriptingSocket._update_value)


    subtypes = ["NONE", "STRING_VALUE"]
    subtype_values = {"NONE": "default_value", "NAMED_ICON": "named_icon"}
    

    def get_color(self, context, node):
        return (0.44, 0.7, 1)

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
