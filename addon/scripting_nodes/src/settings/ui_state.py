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

    # Data panel
    data_filter: bpy.props.StringProperty(
        name="Filter",
        description="Only show properties and variables containing this text",
        default="",
    )

    def update_active_function_index(self, context):
        # Functions are indexed into bpy.data.node_groups directly, not refs
        if not hasattr(context.space_data, "node_tree"):
            return
        if 0 <= self.active_function_index < len(bpy.data.node_groups):
            tree = bpy.data.node_groups[self.active_function_index]
            if getattr(tree, "is_sn", False) and getattr(tree, "is_group", False):
                context.space_data.node_tree = tree

    active_function_index: bpy.props.IntProperty(
        default=0, update=update_active_function_index
    )
