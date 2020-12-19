import bpy


PROPERTY_VAR_TYPES = ["STRING", "INTEGER"]


class SN_PT_GraphPanel(bpy.types.Panel):
    bl_idname = "SN_PT_GraphPanel"
    bl_label = "Graphs"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return context.scene.sn.editing_addon != "NONE" and context.space_data.tree_type == "ScriptingNodesTree"

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()

        row = layout.row(align=False)
        row.template_list("SN_UL_GraphList", "Graphs", addon_tree, "sn_graphs", addon_tree, "sn_graph_index",rows=3)
        col = row.column(align=True)
        col.operator("sn.add_graph", text="", icon="ADD")
        col.operator("sn.remove_graph", text="", icon="REMOVE").index = addon_tree.sn_graph_index


bpy.utils.register_class(SN_PT_GraphPanel)


class SN_PT_VariablePanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_VariablePanel"
    bl_label = "Variables"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 1

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        row = layout.row(align=False)
        col = row.column(align=True)
        col.template_list("SN_UL_VariableList", "Variables", graph_tree, "sn_variables", graph_tree, "sn_variable_index",rows=3)
        if len(graph_tree.sn_variables):
            btn_row = col.row(align=True)
            btn_row.operator("sn.add_getter",icon="SORT_DESC", text="Getter")
            btn_row.operator("sn.add_setter",icon="SORT_ASC", text="Setter")
        col = row.column(align=True)
        col.operator("sn.add_variable", text="", icon="ADD")
        col.operator("sn.remove_variable", text="", icon="REMOVE")
        
        if len(graph_tree.sn_variables):
            layout.separator()
            row = layout.row()
            col = row.column()
            col.use_property_split = True
            col.use_property_decorate = False
            var = graph_tree.sn_variables[graph_tree.sn_variable_index]
            
            col.prop(var,"var_type",text="Type")
            col.separator()
            
            if var.var_type in PROPERTY_VAR_TYPES:
                col.prop(var,"make_property",text="Make Property")
                if var.make_property:
                    col.prop(var,"attach_property_to",text="Attach To")
                col.separator()
            
            if var.var_type == "String":
                col.prop(var,"str_default")
            elif var.var_type == "Integer":
                col.prop(var,"int_default")
            
            row.label(text="",icon="BLANK1")


class SN_PT_IconPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_IconPanel"
    bl_label = "Custom Icons"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 2
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        
        row = layout.row(align=False)
        col = row.column(align=True)
        col.template_list("SN_UL_IconList", "Custom Icons", addon_tree, "sn_icons", addon_tree, "sn_icon_index",rows=3)
        if len(addon_tree.sn_icons):
            col.operator("sn.add_get_icon",icon="SORT_DESC", text="Getter")
        col = row.column(align=True)
        col.operator("sn.add_icon", text="", icon="ADD")
        col.operator("sn.remove_icon", text="", icon="REMOVE")
        
        
        if len(addon_tree.sn_icons):
            col = layout.column()
            row = col.row()
            icon = addon_tree.sn_icons[addon_tree.sn_icon_index]
            row.prop_search(icon, "image", bpy.data, "images", text="")
            row.label(icon="BLANK1")
            
            
class SN_PT_AssetsPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_AssetsPanel"
    bl_label = "Assets"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 3
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        
        row = layout.row(align=False)
        col = row.column(align=True)
        col.template_list("SN_UL_AssetList", "Assets", addon_tree, "sn_assets", addon_tree, "sn_asset_index",rows=3)
        if len(addon_tree.sn_assets) and addon_tree.sn_assets[addon_tree.sn_asset_index].name:
            col.operator("sn.add_get_asset",icon="SORT_DESC", text="Getter")
        col = row.column(align=True)
        col.operator("sn.add_asset", text="", icon="ADD")
        col.operator("sn.remove_asset", text="", icon="REMOVE")
        
        
        if len(addon_tree.sn_assets):
            col = layout.column()
            row = col.row()
            row.prop(addon_tree.sn_assets[addon_tree.sn_asset_index],"path",text="")
            row.label(icon="BLANK1")
        
        
            
            
            
bpy.utils.register_class(SN_PT_VariablePanel)
bpy.utils.register_class(SN_PT_IconPanel)
bpy.utils.register_class(SN_PT_AssetsPanel)