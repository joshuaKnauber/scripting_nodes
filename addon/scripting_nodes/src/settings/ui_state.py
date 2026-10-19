import bpy


class SNA_FileRow(bpy.types.PropertyGroup):
    """A row of the Files list: a folder, tree or script (node_tree/file_list.py)."""

    kind: bpy.props.StringProperty()  # FOLDER, TREE or SCRIPT
    item_id: bpy.props.StringProperty()


class SNA_UISettings(bpy.types.PropertyGroup):
    def update_active_file(self, context):
        from ..node_tree import file_list

        selected = file_list.entry(context.scene, self.active_file)
        space = context.space_data
        if selected and selected.kind == file_list.TREE and hasattr(space, "node_tree"):
            space.node_tree = selected.item

    # the Files list (sidebar), synced by a watcher
    files: bpy.props.CollectionProperty(type=SNA_FileRow)
    active_file: bpy.props.IntProperty(default=-1, update=update_active_file)
