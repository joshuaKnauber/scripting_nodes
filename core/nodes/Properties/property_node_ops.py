import bpy

from .GetPropertyNode import SNA_NodeGetProperty
from .SetPropertyNode import SNA_NodeSetProperty
from ...utils.nodes import get_ref_by_id


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


class SNA_OT_PropertySetter(bpy.types.Operator):
    bl_idname = "sna.property_setter"
    bl_label = "Set Property"
    bl_description = "Set the value of a property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node: bpy.props.StringProperty()
    property_type: bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.node.add_node(
            "INVOKE_DEFAULT", type=SNA_NodeSetProperty.bl_idname, use_transform=True
        )
        node = context.space_data.edit_tree.nodes.active
        property_node = get_ref_by_id(self.node)
        if property_node:
            node.selected_property.name = property_node.name
            node.property_type = self.property_type
        return {"FINISHED"}
