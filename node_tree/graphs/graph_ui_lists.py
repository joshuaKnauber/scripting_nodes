import bpy


class SN_UL_GraphList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.bl_rna.identifier == "ScriptingNodesTree":
            row = layout.row()
            row.label(text="", icon="SCRIPT")
            row.prop(item,"name",emboss=False,text="")
