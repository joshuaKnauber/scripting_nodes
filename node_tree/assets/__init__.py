import bpy


from . import assets_ui_list, create_assets


classes = [assets_ui_list.SN_Asset,
            assets_ui_list.SN_UL_AssetList,
            create_assets.SN_OT_CreateAsset,
            create_assets.SN_OT_RemoveAsset,
            create_assets.SN_OT_AddGetAsset,
            create_assets.SN_OT_MoveAssets]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)