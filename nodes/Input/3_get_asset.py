import bpy
import os
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_GetAssetNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetAssetNode"
    bl_label = "Asset"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    asset: bpy.props.StringProperty(default="",update=SN_ScriptingBaseNode.auto_compile)


    def on_create(self,context):
        self.add_string_output("Path")


    def draw_node(self,context,layout):     
        addon_tree = context.scene.sn.addon_tree()   
        layout.prop_search(self,"asset",addon_tree,"sn_assets",text="",icon="VIEWZOOM")
            

    def code_evaluate(self, context, touched_socket):
        asset_path = ""
        if self.asset and self.asset in self.addon_tree.sn_assets:
            asset_path = self.addon_tree.sn_assets[self.asset].path
            if self.addon_tree.doing_export:
                asset_path = "os.path.join(os.path.dirname(__file__),'assets','" + os.path.basename(asset_path) +"')"
            else:
                asset_path = f"r\"{asset_path}\""
        else:
            self.add_error("No Asset", "No Asset selected")
        return {
            "code": asset_path
        }