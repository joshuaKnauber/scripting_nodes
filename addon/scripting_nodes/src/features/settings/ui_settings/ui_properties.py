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
    active_property_index: bpy.props.IntProperty(default=0)
    active_variable_index: bpy.props.IntProperty(default=0)


