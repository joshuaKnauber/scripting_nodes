import bpy


class SN_UL_PropertyList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon=item.icon)
        row.prop(item, "name", emboss=False, text="")