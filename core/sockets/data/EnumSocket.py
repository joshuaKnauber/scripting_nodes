import bpy

from ..base_socket import ScriptingSocket
from ....utils.enum import make_enum_item


class SNA_EnumItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    value: bpy.props.StringProperty()
    description: bpy.props.StringProperty()


class SNA_EnumSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_EnumSocket"
    bl_label = "Enum"

    items: bpy.props.CollectionProperty(type=SNA_EnumItem)

    def reset_items(self):
        self.items.clear()

    def add_item(self, value, name):
        item = self.items.add()
        item.value = value
        item.name = name
        item.description = f"Input Value: {value}"

    def get_items(self, context):
        items = []
        for i, item in enumerate(self.items):
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
