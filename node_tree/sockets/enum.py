import bpy
from .base_socket import ScriptingSocket



class SN_EnumSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_EnumSocket"
    group = "DATA"
    bl_label = "Enum"


    default_python_value = "\"\""
    default_prop_value = "NONE"

    def get_python_repr(self):
        return f"\"{self.default_value}\""


    items: bpy.props.StringProperty(default="[]",
                                    name="Stringified Items",
                                    description="The items of this enum as a stringified list of strings")


    def get_enum_items(self, _):
        names = eval(self.items)
        if len(names) == 0:
            names = ["NONE"]
        return [(name, name, name) for name in names]

    default_value: bpy.props.EnumProperty(name="Value",
                                            items=get_enum_items,
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)

    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    

    def get_color(self, context, node):
        return (0.44, 0.7, 1)

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, self.subtype_attr, text=text)