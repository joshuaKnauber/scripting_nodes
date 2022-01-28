import bpy
from .base_socket import ScriptingSocket



class SN_EnumSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_EnumSocket"
    group = "DATA"
    bl_label = "Enum"


    default_python_value = "\'\'"
    default_prop_value = ""

    def get_python_repr(self):
        if self.subtype == "ENUM_FLAG":
            return f"{getattr(self, self.subtype_attr)}"
        return f"\'{getattr(self, self.subtype_attr)}\'"


    def get_items(self, _):
        names = eval(self.items)
        items = [("NONE", "NONE", "NONE")]
        if names:
            items = [(name, name, name) for name in names]
        return items


    def _get_value(self):
        value = ScriptingSocket._get_value(self)
        if value:
            return value
        return 0
        

    items: bpy.props.StringProperty(name="Items",
                                    description="Stringified items for this socket",
                                    default="['NONE']")


    default_value: bpy.props.EnumProperty(name="Value",
                                    description="Value of this socket",
                                    items=get_items,
                                    get=_get_value,
                                    set=ScriptingSocket._set_value)


    flag_value: bpy.props.EnumProperty(name="Value",
                                    description="Value of this socket",
                                    items=get_items,
                                    options={"ENUM_FLAG"},
                                    update=ScriptingSocket._update_value)
    
    def on_subtype_update(self):
        self.display_shape = "CIRCLE" if self.subtype == "NONE" else "SQUARE"

    subtypes = ["NONE", "ENUM_FLAG"]
    subtype_values = {"NONE": "default_value", "ENUM_FLAG": "flag_value"}
    

    def get_color(self, context, node):
        if self.subtype == "NONE":
            return (0.44, 0.7, 1)
        return (0.85, 0.15, 1)

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            if self.subtype == "ENUM_FLAG":
                col = layout.column(heading=text)
                col.prop(self, self.subtype_attr, text=text)
            else:
                layout.prop(self, self.subtype_attr, text=text)