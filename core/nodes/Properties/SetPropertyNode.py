import bpy

from ....constants import properties, sockets
from ..base_node import SNA_BaseNode
from ..utils.references import NodePointer, node_search
from .BoolPropertyNode import SNA_NodeBoolProperty


class SNA_NodeSetProperty(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeSetProperty"
    bl_label = "Set Property"
    bl_width_default = 150

    property_type: bpy.props.EnumProperty(
        name="Property Type",
        items=properties.property_type_items,
        update=lambda self, _: self.mark_dirty(),
    )
    selected_property: bpy.props.PointerProperty(
        type=NodePointer,
        name="Panel",
        description="Property to set",
        update=lambda self, _: self.mark_dirty(),
    )

    def on_create(self):
        self.add_input(sockets.EXECUTE)
        inp = self.add_input(sockets.PROPERTY, "Property")
        inp.make_disabled()
        self.add_input(sockets.DATA, "Value")
        self.add_output(sockets.EXECUTE)

    def on_reference_update(self, property_node: bpy.types.Node | None):
        if property_node:
            self.inputs["Value"].name = property_node.source_type
            self.convert_socket(
                self.inputs["Value"],
                sockets.SOCKET_IDNAMES[properties.NODES[property_node.bl_idname]],
            )
        self.mark_dirty()

    def draw_label(self):
        if self.selected_property.node:
            return self.selected_property.name
        return "Set Property"

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row(align=True)
        if not self.inputs["Property"].show_editable:
            row.prop(self, "property_type", text="", icon_only=True)
        else:
            row.prop(self, "property_type", icon_only=True)
        node_search(row, self.selected_property, SNA_NodeBoolProperty.bl_idname)

    def generate(self, context, trigger):
        if not self.selected_property.node:
            return

        # identifier = self.selected_property.node.identifier()

        # self.inputs[0].set_meta("type", self.selected_property.node.source_type)
        # self.outputs["Property"].set_meta("parent", self.inputs[0].get_code())
        # self.outputs["Property"].set_meta("identifier", identifier)

        # self.outputs["Property"].code = f"{self.inputs[0].get_code()}.{identifier}"
        # self.outputs["Value"].code = f"{self.inputs[0].get_code()}.{identifier}"
