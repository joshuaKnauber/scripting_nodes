import bpy


class SNA_UISettings(bpy.types.PropertyGroup):

    def update_active_ntree_index(self, context):
        if (
            self.active_ntree_index < len(bpy.data.node_groups)
            and self.active_ntree_index >= 0
        ):
            context.space_data.node_tree = bpy.data.node_groups[self.active_ntree_index]

    active_ntree_index: bpy.props.IntProperty(
        default=0, update=update_active_ntree_index
    )

    # Blend Data browser properties
    blend_data_search: bpy.props.StringProperty(
        name="Search",
        description="Search for properties in Blender data",
        default="",
    )

    # Data panel - active indices for filtered lists
    def update_active_property_index(self, context):
        sna = context.scene.sna
        if 0 <= self.active_property_index < len(sna.references):
            ref = sna.references[self.active_property_index]
            if ref.node:
                bpy.ops.sna.go_to_node(node_id=ref.node.id)

    def update_active_variable_index(self, context):
        sna = context.scene.sna
        if 0 <= self.active_variable_index < len(sna.references):
            ref = sna.references[self.active_variable_index]
            if ref.node:
                bpy.ops.sna.go_to_node(node_id=ref.node.id)

    active_property_index: bpy.props.IntProperty(
        default=0, update=update_active_property_index
    )
    active_variable_index: bpy.props.IntProperty(
        default=0, update=update_active_variable_index
    )
