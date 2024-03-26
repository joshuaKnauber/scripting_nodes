import bpy

from ...utils.is_serpens import in_sn_tree
from ..ui_lists.properties_list import SNA_UL_PropertiesList


class SNA_PT_InspectorPanel(bpy.types.Panel):
    bl_idname = "SNA_PT_FileInfoPanel"
    bl_label = "Inspector"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        pass


class SNA_PT_SearchPanel(bpy.types.Panel):
    bl_idname = "SNA_PT_SearchPanel"
    bl_parent_id = SNA_PT_InspectorPanel.bl_idname
    bl_label = "Search"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED", "HEADER_LAYOUT_EXPAND"}
    bl_order = 0

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sna = context.scene.sna
        layout.prop(sna, "node_search", icon="VIEWZOOM", text="")


class SNA_PT_PropertyPanel(bpy.types.Panel):
    bl_idname = "SNA_PT_PropertyPanel"
    bl_parent_id = SNA_PT_InspectorPanel.bl_idname
    bl_label = "Properties"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 1

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sna = context.scene.sna

        main_col = layout.column(align=True)
        main_col.prop(sna, "property_type", text="")
        coll = sna.references.get_collection(sna.property_type)
        if coll:
            main_col.template_list(
                SNA_UL_PropertiesList.bl_idname,
                "sn_properties",
                coll,
                "nodes",
                sna,
                "active_property_index",
            )
        else:
            main_col.label(text="No properties found", icon="INFO")


class SNA_PT_VariablePanel(bpy.types.Panel):
    bl_idname = "SNA_PT_VariablePanel"
    bl_parent_id = SNA_PT_InspectorPanel.bl_idname
    bl_label = "Variables"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sna = context.scene.sna
        ntree = context.space_data.node_tree


class SNA_PT_FunctionsPanel(bpy.types.Panel):
    bl_idname = "SNA_PT_FunctionsPanel"
    bl_parent_id = SNA_PT_InspectorPanel.bl_idname
    bl_label = "Functions"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 3

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sna = context.scene.sna
        ntree = context.space_data.node_tree


class SNA_PT_StatsPanel(bpy.types.Panel):
    bl_idname = "SNA_PT_StatsPanel"
    bl_parent_id = SNA_PT_InspectorPanel.bl_idname
    bl_label = "Statistics"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED", "HEADER_LAYOUT_EXPAND"}
    bl_order = 4

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sna = context.scene.sna

        count_ntrees = 0
        count_nodes = 0
        for ntree in bpy.data.node_groups:
            if getattr(ntree, "is_sn_ntree", False):
                count_ntrees += 1
                count_nodes += len(ntree.nodes)

        layout.label(text=f"Node Trees: {count_ntrees}")
        layout.label(text=f"Nodes: {count_nodes}")
