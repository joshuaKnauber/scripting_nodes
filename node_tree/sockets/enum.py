import bpy
from .base_socket import ScriptingSocket



class SocketEnumItem(bpy.types.PropertyGroup):
    
    def update_name(self, context):
        node = context.space_data.node_tree.nodes.active
        for socket in list(node.inputs) + list(node.outputs):
            if socket.bl_label == "Enum" or socket.bl_label == "Enum Set":
                for item in socket.custom_items:
                    if item == self:
                        node.on_socket_type_change(socket)
                        return
        
    name: bpy.props.StringProperty(name="Name", default="New Item",
                                description="Name of this enum item",
                                update=update_name)



_item_map = dict()

class SN_EnumSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_EnumSocket"
    group = "DATA"
    bl_label = "Enum"


    default_python_value = "\'\'"
    default_prop_value = ""

    def get_python_repr(self):
        return f"\'{getattr(self, self.subtype_attr)}\'"


    def make_enum_item(self, _id, name, descr, preview_id, uid):
        lookup = str(_id)+"\\0"+str(name)+"\\0"+str(descr)+"\\0"+str(preview_id)+"\\0"+str(uid)
        if not lookup in _item_map:
            _item_map[lookup] = (_id, name, descr, preview_id, uid)
        return _item_map[lookup]
    
    def get_items(self, _):
        if self.subtype == "CUSTOM_ITEMS":
            items = [self.make_enum_item(item.name, item.name, item.name, 0, i) for i, item  in enumerate(self.custom_items)]
            if items: return items
        else:
            names = eval(self.items)
            if names: return [self.make_enum_item(name, name, name, 0, i) for i, name in enumerate(names)]
        return [("NONE", "NONE", "NONE")]


    def _get_value(self):
        value = ScriptingSocket._get_value(self)
        if value:
            return value
        return 0
    
    
    custom_items: bpy.props.CollectionProperty(type=SocketEnumItem)
    
    
    custom_items_editable: bpy.props.BoolProperty(default=True,
                                    name="Editable Custom Items",
                                    description="Lets you edit the custom items")
        

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

    def draw_socket(self, context, layout, node, text, minimal=False):
        if not minimal:
            if self.is_output or self.is_linked:
                layout.label(text=text)
            else:
                layout.prop(self, self.subtype_attr, text=text)
        if self.subtype == "CUSTOM_ITEMS" and self.custom_items_editable:
            op = layout.operator("sn.edit_enum_items", text="", icon="GREASEPENCIL")
            op.node = self.node.name
            op.is_output = self.is_output
            op.index = self.index
