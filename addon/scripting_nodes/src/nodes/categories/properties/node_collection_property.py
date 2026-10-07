import bpy

from ._property_base import PropertyNode
from .node_pointer_property import GroupTypeMixin


class SNA_Node_CollectionProperty(GroupTypeMixin, PropertyNode, bpy.types.Node):
    """A list of Property Group items. Change it with the Collection nodes,
    read it with Get Property."""

    bl_idname = "SNA_Node_CollectionProperty"
    bl_label = "Collection Property"
    bpy_type = "CollectionProperty"
    data_type = "ScriptingBlendDataSocket"
    supported_options = ("HIDDEN", "SKIP_SAVE", "LIBRARY_EDITABLE")
    has_update = False  # CollectionProperty has no update callback

    prop_label: bpy.props.StringProperty(name="Label", default="My Collection")

    def property_args(self, ctx):
        return [f"type={self.group_type(ctx)}"]

    def emit(self, ctx):
        self.group_type(ctx)  # show a missing group on this node
        super().emit(ctx)

    def draw_node(self, context, layout):
        self.draw_reference_prop(layout, "group", text="Group")
