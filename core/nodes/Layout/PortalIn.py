import bpy

from ...utils.nodes import get_ref_by_id

from ....constants import sockets
from ..base_node import SNA_BaseNode


class SNA_OT_OutPortal(bpy.types.Operator):
    bl_idname = "sna.out_portal"
    bl_label = "Out Portal"
    bl_description = "Get Out Portal"

    node: bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.node.add_node(
            "INVOKE_DEFAULT", type="SNA_NodePortalOut", use_transform=True
        )
        node = context.space_data.edit_tree.nodes.active
        property_node = get_ref_by_id(self.node)
        if property_node:
            node.portal.name = property_node.name
            node.hide = True
        return {"FINISHED"}


class SNA_NodePortalIn(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodePortalIn"
    bl_label = "Portal In"
    bl_width_default = 100

    def update_color(self, context):
        self.color = self.node_color
        self.mark_dirty()

    node_color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        default=(0.5, 0.5, 0.5),
        min=0,
        max=1,
        update=update_color,
    )

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row(align=True)
        row.prop(self, "name", text="")
        split = row.split(factor=0.8, align=True)
        subsplit = split.split(factor=0.5, align=True)
        subsplit.prop(self, "node_color", text="")
        op = subsplit.operator("sna.out_portal", text="", icon="SORT_DESC")
        op.node = self.id

    def draw_label(self):
        return self.name

    def on_create(self):
        self.add_input(sockets.DATA)
        self.use_custom_color = True
