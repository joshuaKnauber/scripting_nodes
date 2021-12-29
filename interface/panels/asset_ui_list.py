import bpy
import os



class SN_UL_AssetList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon="ASSET_MANAGER")
        row.prop(item, "name", text="", emboss=False)