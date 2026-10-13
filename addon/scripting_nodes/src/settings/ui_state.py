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

    def update_active_function_index(self, context):
        # Functions are indexed into bpy.data.node_groups directly, not refs
        if not hasattr(context.space_data, "node_tree"):
            return
        if 0 <= self.active_function_index < len(bpy.data.node_groups):
            tree = bpy.data.node_groups[self.active_function_index]
            if getattr(tree, "is_sn", False) and tree.is_function:
                context.space_data.node_tree = tree

    active_function_index: bpy.props.IntProperty(
        default=0, update=update_active_function_index
    )

    # Data explorer (blend_data/ui/explorer_panel.py)
    explorer_path: bpy.props.StringProperty(
        name="Explorer Path",
        description="Where the data explorer is (a Python path)",
    )
    explorer_filter: bpy.props.StringProperty(
        name="Filter",
        description="Only show entries containing this text",
        options={"TEXTEDIT_UPDATE"},
    )
    explorer_show_all: bpy.props.BoolProperty(
        name="Show Empty and Internal",
        description="Also show empty pointers and lists, and read-only values",
    )
