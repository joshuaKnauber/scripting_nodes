import bpy
from bpy_extras.io_utils import ImportHelper
import os



class SN_OT_AddAsset(bpy.types.Operator, ImportHelper):
    bl_idname = "sn.add_asset"
    bl_label = "Add Asset"
    bl_description = "Adds a asset to the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    def execute(self, context):
        _, extension = os.path.splitext(self.filepath)
        if extension:
            sn = context.scene.sn
            new_asset = sn.assets.add()
            new_asset.path = self.filepath
            for index, asset in enumerate(sn.assets):
                if asset == new_asset:
                    sn.asset_index = index
        return {"FINISHED"}



class SN_OT_RemoveAsset(bpy.types.Operator):
    bl_idname = "sn.remove_asset"
    bl_label = "Remove Asset"
    bl_description = "Removes this asset from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.scene.sn.asset_index < len(context.scene.sn.assets)

    def execute(self, context):
        sn = context.scene.sn
        asset = sn.assets[sn.asset_index]
        # remove removed from asset nodes
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if node.bl_idname == "SN_AssetNode":
                        if node.asset == asset.name:
                            node.asset = ""
        # remove asset
        sn.assets.remove(sn.asset_index)
        sn.asset_index -= 1
        return {"FINISHED"}
    
    
    
class SN_OT_FindNode(bpy.types.Operator):
    bl_idname = "sn.find_node"
    bl_label = "Find Node"
    bl_description = "Find Node"
    bl_options = {"REGISTER", "INTERNAL"}
    
    node_tree: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    node: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    def execute(self, context):
        ntree = bpy.data.node_groups[self.node_tree]
        for node in ntree.nodes:
            node.select = node.name == self.node
        bpy.ops.node.view_selected("INVOKE_DEFAULT")
        return {"FINISHED"}



class SN_OT_FindAsset(bpy.types.Operator):
    bl_idname = "sn.find_asset"
    bl_label = "Find Asset"
    bl_description = "Finds this asset in the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        
        empty_nodes = []
        if context.scene.sn.asset_index < len(context.scene.sn.assets):
            asset = context.scene.sn.assets[context.scene.sn.asset_index]
            
            found_nodes = False
            col = layout.column()
            row = col.row()
            row.enabled = False
            row.label(text=asset.name)
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    for node in ntree.nodes:
                        if node.bl_idname == "SN_AssetNode":
                            if node.asset == asset.name:
                                found_nodes = True
                                op = col.operator("sn.find_node", text=node.name, icon="RESTRICT_SELECT_OFF")
                                op.node_tree = ntree.name
                                op.node = node.name
                            elif not node.asset:
                                empty_nodes.append(node)
            
            if not found_nodes:
                col.label(text="No nodes found for this asset", icon="INFO")
        
        col = layout.column()
        row = col.row()
        row.label(text="Empty Asset Nodes")
        row.enabled = False
        if len(empty_nodes) > 0:
            for node in empty_nodes:
                op = col.operator("sn.find_node", text=node.name, icon="RESTRICT_SELECT_OFF")
                op.node_tree = ntree.name
                op.node = node.name
        else:
            col.label(text="No nodes found for this asset", icon="INFO")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)