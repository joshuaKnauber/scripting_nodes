import bpy

from ...utils.is_serpens import in_sn_tree
from ..ui_lists.properties_list import SN_UL_PropertiesList


class SN_PT_FileInfoPanel(bpy.types.Panel):
    bl_idname = "SN_PT_FileInfoPanel"
    bl_label = "Inspector"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        pass


class SN_PT_SearchPanel(bpy.types.Panel):
    bl_idname = "SN_PT_SearchPanel"
    bl_parent_id = SN_PT_FileInfoPanel.bl_idname
    bl_label = "Search"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED", "HEADER_LAYOUT_EXPAND"}
    bl_order = 0

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn
        layout.prop(sn, "node_search", icon="VIEWZOOM", text="")


class SN_PT_PropertyPanel(bpy.types.Panel):
    bl_idname = "SN_PT_PropertyPanel"
    bl_parent_id = SN_PT_FileInfoPanel.bl_idname
    bl_label = "Properties"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 1

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn

        main_col = layout.column(align=True)
        main_col.prop(sn, "property_type", text="")
        coll = sn.references.get_collection(sn.property_type)
        if coll:
            main_col.template_list(SN_UL_PropertiesList.bl_idname, "sn_properties", coll, "nodes", sn, "active_property_index")
        else:
            main_col.label(text="No properties found", icon="INFO")


class SN_PT_VariablePanel(bpy.types.Panel):
    bl_idname = "SN_PT_VariablePanel"
    bl_parent_id = SN_PT_FileInfoPanel.bl_idname
    bl_label = "Variables"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn
        ntree = context.space_data.node_tree


class SN_PT_FunctionsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_FunctionsPanel"
    bl_parent_id = SN_PT_FileInfoPanel.bl_idname
    bl_label = "Functions"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 3

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn
        ntree = context.space_data.node_tree


class SN_PT_StatsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_StatsPanel"
    bl_parent_id = SN_PT_FileInfoPanel.bl_idname
    bl_label = "Statistics"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED", "HEADER_LAYOUT_EXPAND"}
    bl_order = 4

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn

        count_ntrees = 0
        count_nodes = 0
        for ntree in bpy.data.node_groups:
            if getattr(ntree, "is_sn", False):
                count_ntrees += 1
                count_nodes += len(ntree.nodes)

        layout.label(text=f"Node Trees: {count_ntrees}")
        layout.label(text=f"Nodes: {count_nodes}")
