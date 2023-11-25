import typing

import bpy

from ....constants import properties, sockets
from ..base_node import SNA_BaseNode
from ..utils.references import NodePointer, node_search
from .BoolPropertyNode import SNA_NodeBoolProperty


class SNA_NodeGetProperty(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeGetProperty"
    bl_label = "Get Property"

    property_type: bpy.props.EnumProperty(
        items=properties.property_type_items, update=lambda self, _: self.mark_dirty()
    )
    selected_property: bpy.props.PointerProperty(
        type=NodePointer,
        name="Panel",
        description="Panel to be displayed",
        update=lambda self, _: self.mark_dirty(),
    )

    def on_create(self):
        self.add_input(sockets.PROPERTY, "Source")
        self.add_output(sockets.PROPERTY, "Property")
        self.add_output(sockets.BOOLEAN, "Value")

    def on_reference_update(self, property_node: bpy.types.Node):
        self.inputs[0].name = property_node.source_type
        self.inputs[0].set_meta("type", property_node.source_type)
        self.mark_dirty()

    def draw_label(self):
        if self.selected_property.node:
            return self.selected_property.name
        return "Get Property"

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row(align=True)
        row.prop(self, "property_type", text="", icon_only=True)
        node_search(row, self.selected_property, SNA_NodeBoolProperty.bl_idname)

    def generate(self, context, trigger):
        if not self.selected_property.node:
            return

        identifier = self.selected_property.node.identifier()
        self.outputs["Property"].code = f"{self.inputs[0].get_code()}.{identifier}"
        self.outputs["Property"].set_meta("data", "bpy.context.scene")
        self.outputs["Property"].set_meta("identifier", identifier)

        self.outputs["Value"].code = f"bpy.context.scene.{identifier}"
