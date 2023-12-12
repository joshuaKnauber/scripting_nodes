import bpy

from .GetPropertyNode import SNA_NodeGetProperty
from ...utils.nodes import get_ref_by_id
from ..utils.references import get_references_to_node


class SNA_OT_PropertyGetter(bpy.types.Operator):
    bl_idname = "sna.property_getter"
    bl_label = "Get Property"
    bl_description = "Get the value of a property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node: bpy.props.StringProperty()
    property_type: bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.node.add_node(
            "INVOKE_DEFAULT", type=SNA_NodeGetProperty.bl_idname, use_transform=True
        )
        node = context.space_data.edit_tree.nodes.active
        property_node = get_ref_by_id(self.node)
        if property_node:
            node.selected_property.name = property_node.name
            node.property_type = self.property_type
        return {"FINISHED"}
