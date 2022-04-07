import bpy
from .base_socket import ScriptingSocket



class SocketEnumItem(bpy.types.PropertyGroup):
    
    def update(self, context):
        pass
        
    name: bpy.props.StringProperty(name="Name", default="New Item",
                                description="Name of this enum item",
                                update=update)



class SN_EnumSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_EnumSocket"
    group = "DATA"
    bl_label = "Enum"


    default_python_value = "\'\'"
    default_prop_value = ""

    def get_python_repr(self):
        return f"\'{getattr(self, self.subtype_attr)}\'"


    def get_items(self, _):
        if self.subtype == "CUSTOM_ITEMS":
            items = [(item.name, item.name, item.name, i) for i, item  in enumerate(self.custom_items)]
            return items
        else:
            names = eval(self.items)
            if names:
                return [(name, name, name, i) for i, name in enumerate(names)]
        return [("NONE", "NONE", "NONE")]


    def _get_value(self):
        value = ScriptingSocket._get_value(self)
        if value:
            return value
        return 0
    
    
    custom_items: bpy.props.CollectionProperty(type=SocketEnumItem)
        

    items: bpy.props.StringProperty(name="Items",
                                    description="Stringified items for this socket",
                                    default="['NONE']")


    default_value: bpy.props.EnumProperty(name="Value",
                                    description="Value of this socket",
                                    items=get_items,
                                    get=_get_value,
                                    set=ScriptingSocket._set_value)


    subtypes = ["NONE", "CUSTOM_ITEMS"]
    subtype_values = {"NONE": "default_value", "CUSTOM_ITEMS": "default_value"}
    

    def get_color(self, context, node):
        return (0.44, 0.7, 1)

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, self.subtype_attr, text=text)
        op = layout.operator("sn.edit_enum_items", text="", icon="GREASEPENCIL")
        op.node = self.node.name
        op.is_output = self.is_output
        op.index = self.index