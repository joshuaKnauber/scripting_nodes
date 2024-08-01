import bpy

from ...utils.node_tree import get_node_tree_by_id
from ..base_socket import ScriptingSocket
from ....utils.enum import make_enum_item


class SNA_EnumItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    value: bpy.props.StringProperty()
    description: bpy.props.StringProperty()


class SNA_EnumSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_EnumSocket"
    bl_label = "Enum"

    enum_items: bpy.props.CollectionProperty(type=SNA_EnumItem)

    def reset_items(self):
        self.enum_items.clear()

    def add_item(self, value, name):
        item = self.enum_items.add()
        item.value = value
        item.name = name
        item.description = f"Input Value: {value}"

    def get_items(self, context):
        # select sockets collection or group interface socket collection
        items_collection = self.enum_items
        if self.node_is_group():
            items_collection = self.group_interface_socket().enum_items
        # get items
        items = []
        for i, item in enumerate(items_collection):
            items.append(make_enum_item(item.value, item.name, item.description, 0, i))
        return items

    value: bpy.props.EnumProperty(
        items=get_items,
        update=lambda self, _: self.node.mark_dirty(),
    )

    def _python_value(self):
        if self.is_output:
            return self.code if self.code else "''"
        return f"'{self.value}'"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.44, 0.7, 1, 1)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output:
            if self.show_editable:
                layout.prop(
                    self,
                    "editable",
                    text="",
                    icon="HIDE_OFF" if self.editable else "HIDE_ON",
                    emboss=False,
                )
            if self.editable and not self.is_linked:
                layout.prop(self, "value", text=text)
            else:
                layout.label(text=text)
        else:
            layout.label(text=text)


class SNA_AddSocketEnumItem(bpy.types.Operator):
    bl_idname = "sna.add_socket_enum_item"
    bl_label = "Add Enum Item"
    bl_description = "Add an enum item to this socket"
    bl_options = {"REGISTER", "UNDO"}

    node_tree_id: bpy.props.StringProperty()
    position: bpy.props.IntProperty()

    def execute(self, context):
        ntree = get_node_tree_by_id(self.node_tree_id)
        if ntree:
            socket = ntree.interface.items_tree[self.position]
            socket.enum_items.add()
        return {"FINISHED"}


class SNA_DeleteSocketEnumItem(bpy.types.Operator):
    bl_idname = "sna.delete_socket_enum_item"
    bl_label = "Delete Enum Item"
    bl_description = "Delete the selected enum item"
    bl_options = {"REGISTER", "UNDO"}

    node_tree_id: bpy.props.StringProperty()
    position: bpy.props.IntProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        ntree = get_node_tree_by_id(self.node_tree_id)
        if ntree:
            socket = ntree.interface.items_tree[self.position]
            socket.enum_items.remove(self.index)
        return {"FINISHED"}


class SNA_EnumSocketInterface(bpy.types.NodeTreeInterfaceSocket):

    bl_idname = "SNA_EnumSocketInterface"
    bl_socket_idname = "SNA_EnumSocket"
    bl_label = "Enum"

    enum_items: bpy.props.CollectionProperty(type=SNA_EnumItem)

    def add_item(self, value, name):
        item = self.enum_items.add()
        item.value = value
        item.name = name
        item.description = f"Input Value: {value}"

    def draw(self, context, layout):
        col = layout.column(align=True)
        for i, item in enumerate(self.enum_items):
            box = col.box()
            boxcol = box.column(align=True)
            row = boxcol.row()
            row.prop(item, "name", text="")
            op = row.operator(
                "sna.delete_socket_enum_item", text="", icon="TRASH", emboss=False
            )
            op.node_tree_id = self.id_data.id
            op.position = self.position
            op.index = i
            boxcol.prop(item, "value", text="Value")
            boxcol.prop(item, "description", text="Description")
        op = layout.operator("sna.add_socket_enum_item", text="Add Item", icon="ADD")
        op.node_tree_id = self.id_data.id
        op.position = self.position


def register():
    bpy.utils.register_class(SNA_EnumSocketInterface)


def unregister():
    bpy.utils.unregister_class(SNA_EnumSocketInterface)
