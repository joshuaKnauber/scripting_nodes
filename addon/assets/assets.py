import bpy
import os


class SN_AssetProperties(bpy.types.PropertyGroup):

    def get_to_update(self, asset_name):
        """Get nodes that reference this asset by name"""
        to_update = []
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if node.bl_idname == "SN_AssetNode":
                        if node.asset == asset_name:
                            to_update.append(node)
        return to_update

    def update_file_path(self, context):
        abs_path = bpy.path.abspath(self.path)
        if not self.path == abs_path:
            self.path = abs_path
        else:
            if self.name == "Asset" and self.path:
                self.name = os.path.basename(self.path)
        for node in self.get_to_update(self.name):
            node._evaluate(context)

    def update_name(self, context):
        """Update asset nodes when name changes"""
        prev_name = self.prev_name
        new_name = self.name

        if prev_name and prev_name != new_name:
            for node in self.get_to_update(prev_name):
                node.asset = new_name

        self.prev_name = new_name

    # Track previous name for reference updates
    prev_name: bpy.props.StringProperty()

    name: bpy.props.StringProperty(
        name="Name",
        description="Name of the asset",
        default="Asset",
        update=update_name,
    )

    path: bpy.props.StringProperty(
        name="Path",
        description="Path to the asset file",
        subtype="FILE_PATH",
        update=update_file_path,
    )
