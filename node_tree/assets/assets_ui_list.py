import bpy
import os


class SN_Asset(bpy.types.PropertyGroup):

    def update_path(self,context):
        if not self.path == bpy.path.abspath(self.path):
            self.path = bpy.path.abspath(self.path)
        self.name = os.path.basename(self.path)

    path: bpy.props.StringProperty(name="Path",
                                   description="Asset",
                                   subtype="FILE_PATH",
                                   update=update_path)
    
    name: bpy.props.StringProperty()



class SN_UL_AssetList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        if item.path:
            row.label(text="", icon="ASSET_MANAGER")
        else:
            row.label(text="", icon="ERROR")
        
        if item.path:
            row.label(text=os.path.basename(item.path))
        else:
            row.label(text="No Path")
