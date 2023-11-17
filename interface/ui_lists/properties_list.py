import bpy


class SNA_UL_PropertiesList(bpy.types.UIList):
    bl_idname = "SNA_UL_PropertiesList"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        layout.prop(item, "name", text="", emboss=False)
