import bpy



class SN_PT_AssetsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AssetsPanel"
    bl_label = "Assets"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 2
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        
        # draw asset list
        row = layout.row(align=False)
        col = row.column(align=True)
        col.template_list("SN_UL_AssetList", "Assets", sn, "assets", sn, "asset_index", rows=3)
        op = col.operator("node.add_node", text="Add Node", icon="ADD")
        op.type = "SN_AssetNode"
        op.use_transform = True
        col = row.column(align=True)
        col.operator("sn.add_asset", text="", icon="ADD")
        col.operator("sn.find_asset", text="", icon="VIEWZOOM")
        col.operator("sn.remove_asset", text="", icon="REMOVE")

        # draw asset settings
        if sn.asset_index < len(sn.assets):
            asset = sn.assets[sn.asset_index]
            col = layout.column()
            col.use_property_split = True
            col.use_property_decorate = False

            col.prop(asset, "path", text="")