import bpy
import os



class SN_AssetProperties(bpy.types.PropertyGroup):

    def update_file_path(self, context):
        if not self.path == bpy.path.abspath(self.path):
            self["path"] = bpy.path.abspath(self.path)
        else:
            if self.name == "Asset" and self.path:
                self.name = os.path.basename(self.path)

    def get_asset_name(self):
        return self.get("name", "Asset")
    
    def set_asset_name(self, new_name):
        # update asset nodes that had this asset
        to_update = []
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if node.bl_idname == "SN_AssetNode":
                        if node.asset == self.name:
                            to_update.append(node)
        self["name"] = new_name
        for node in to_update:
            node.asset = new_name
        

    name: bpy.props.StringProperty(name="Name",
                                description="Name of the asset",
                                default="Asset",
                                get=get_asset_name,
                                set=set_asset_name)
    
    path: bpy.props.StringProperty(name="Path",
                                description="Path to the asset file",
                                subtype="FILE_PATH",
                                update=update_file_path)