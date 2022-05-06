import bpy



class SN_UL_GraphList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon="SCRIPT")
        row.prop(item, "name", emboss=False, text="")

    def filter_items(self, context, data, propname):
        node_trees = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        flt_flags = helper_funcs.filter_items_by_name("ScriptingNodesTree", self.bitflag_filter_item, node_trees, "bl_idname", reverse=False)

        _sort = [(idx, frame) for idx, frame in enumerate(bpy.data.node_groups)]
        flt_neworder = helper_funcs.sort_items_helper(_sort, lambda e: getattr(e[1], "index", 0), False)

        return flt_flags, flt_neworder
