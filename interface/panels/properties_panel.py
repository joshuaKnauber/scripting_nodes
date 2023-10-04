import bpy

from ...utils.is_serpens import in_sn_tree
from ..ui_lists.properties_list import SN_UL_PropertiesList


class SN_PT_PropertyPanel(bpy.types.Panel):
    bl_idname = "SN_PT_PropertyPanel"
    bl_label = "Properties"
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

        main_col = layout.column(align=True)
        main_col.prop(sn, "property_type", text="")
        coll = sn.references.get_collection(sn.property_type)
        if coll:
            main_col.template_list(SN_UL_PropertiesList.bl_idname, "sn_properties", coll, "nodes", sn, "active_property_index")
        else:
            main_col.label(text="No properties found", icon="INFO")
