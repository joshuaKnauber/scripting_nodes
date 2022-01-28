import bpy


class SN_UL_VariableList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon=item.icon)
        row.prop(item, "name", emboss=False, text="")
        row.operator("sn.copy_python_name", text="", icon="COPYDOWN", emboss=False).name = item.data_path