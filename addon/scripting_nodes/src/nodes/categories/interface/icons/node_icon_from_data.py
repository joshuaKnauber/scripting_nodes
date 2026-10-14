import bpy

from .....sockets.spec import BlendData, Icon, String
from ....base_node import ScriptingBaseNode


class SNA_Node_IconFromData(ScriptingBaseNode, bpy.types.Node):
    """The icon Blender shows for data (an object's type, a material's
    preview, ...) or for an item of an enum property."""

    bl_idname = "SNA_Node_IconFromData"
    bl_label = "Icon from Data"
    sn_outputs = [Icon("icon", "Icon")]
    sn_header_props = ("source",)

    source: bpy.props.EnumProperty(
        name="Source",
        items=[
            ("DATA", "Data", "The icon of a data-block, e.g. an object or material"),
            ("ENUM", "Enum Item", "The icon of an item of an enum property"),
        ],
    )

    def socket_specs(self):
        inputs = [BlendData("data", "Data")]
        if self.source == "ENUM":
            inputs += [String("property", "Property"), String("item", "Item")]
        return inputs, self.sn_outputs

    def emit(self, ctx):
        data = ctx.input("data")
        if self.source == "ENUM":
            prop, item = ctx.input("property"), ctx.input("item")
            icon = f"bpy.types.UILayout.enum_item_icon({data}, {prop}, {item})"
        else:
            icon = f"bpy.types.UILayout.icon({data})"
        # no data (no active object, ...) draws no icon instead of failing
        ctx.output("icon", f"{icon} if {data} is not None else 0")
