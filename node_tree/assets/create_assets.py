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