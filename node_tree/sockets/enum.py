import bpy
from .base_socket import ScriptingSocket



class SN_EnumSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_EnumSocket"
    group = "DATA"
    bl_label = "Enum"


    default_python_value = "\'NONE\'"
    default_prop_value = "NONE"

    def get_python_repr(self):
        return f"\'{getattr(self, self.subtype_attr)}\'"


    def get_items(self, _):
        names = eval(self.items)
        items = [("NONE", "NONE", "NONE")]
        if names:
            items = [(name, name, name) for name in names]
        return items

    items: bpy.props.StringProperty(name="Items",
                                    description="Stringified items for this socket",
                                    default="['NONE']")


    def _get_value(self):
        value = ScriptingSocket._get_value(self)
        return self.get_items(None)[value]

    def _set_value(self, value):
        value = self.get_items(None)[value]
        ScriptingSocket._set_value(self, value)


    default_value: bpy.props.EnumProperty(name="Value",
                                    description="Value of this socket",
                                    items=get_items,
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