import bpy


class SN_OT_CreateAsset(bpy.types.Operator):
    bl_idname = "sn.add_asset"
    bl_label = "Add Asset"
    bl_description = "Adds a new asset to this addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()

        addon_tree.sn_assets.add()
        
        addon_tree.sn_asset_index = len(addon_tree.sn_assets)-1
        return {"FINISHED"}



class SN_OT_RemoveAsset(bpy.types.Operator):
    bl_idname = "sn.remove_asset"
    bl_label = "Remove Asset"
    bl_description = "Removes this asset from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        addon_tree = context.scene.sn.addon_tree()
        return len(addon_tree.sn_assets) > 0

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        addon_tree.sn_assets.remove(addon_tree.sn_asset_index)
        if addon_tree.sn_asset_index > 0:
            addon_tree.sn_asset_index -= 1
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    
    
class SN_OT_AddGetAsset(bpy.types.Operator):
    bl_idname = "sn.add_get_asset"
    bl_label = "Add Getter"
    bl_description = "Adds a node which gives you the path to this asset"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        bpy.ops.node.add_node("INVOKE_DEFAULT",type="SN_GetAssetNode",use_transform=True)
        graph_tree.nodes.active.asset = addon_tree.sn_assets[addon_tree.sn_asset_index].name
        return {"FINISHED"}
    
    
    
class SN_OT_MoveAssets(bpy.types.Operator):
    bl_idname = "sn.move_asset"
    bl_label = "Move Assets"
    bl_description = "Moves this asset"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    up: bpy.props.BoolProperty()

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        
        if (self.up):
            addon_tree.sn_assets.move(addon_tree.sn_asset_index,addon_tree.sn_asset_index-1)
            addon_tree.sn_asset_index -= 1
        else:
            addon_tree.sn_assets.move(addon_tree.sn_asset_index,addon_tree.sn_asset_index+1)
            addon_tree.sn_asset_index += 1
        return {"FINISHED"}