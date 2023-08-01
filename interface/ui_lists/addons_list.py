import bpy


class SN_UL_AddonsList(bpy.types.UIList):
    bl_idname = "SN_UL_AddonsList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False)
