import bpy

from ....constants import properties, sockets
from ..base_node import SN_BaseNode
from ..Properties.BoolPropertyNode import SN_BoolPropertyNode
from ..utils.references import NodePointer, node_search


class SN_GetPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_GetPropertyNode"
    bl_label = "Get Property"

    property_type: bpy.props.EnumProperty(items=properties.property_type_items)

    selected_property: bpy.props.PointerProperty(type=NodePointer)

    def on_create(self):
        self.add_input(sockets.PROPERTY, "Source")
        self.add_output(sockets.PROPERTY, "Property")
        self.add_output(sockets.BOOLEAN, "Property Value")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row(align=True)
        row.prop(self, "property_type", text="", icon_only=True)
        node_search(row, self.selected_property, SN_BoolPropertyNode.bl_idname)

    def generate(self, context):
        pass
