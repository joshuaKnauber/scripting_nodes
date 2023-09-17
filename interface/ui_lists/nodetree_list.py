import bpy


class SN_UL_NodeTreesList(bpy.types.UIList):
    bl_idname = "SN_UL_NodeTreesList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False)

    def filter_items(self, context, data, propname):
        # TODO
        groups = bpy.data.node_groups
        helper_funcs = bpy.types.UI_UL_list

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # Filtering by name
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, groups, "name",
                                                          reverse=self.use_filter_name_reverse)
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(groups)

        # Filter by node tree type
        for i, ntree in enumerate(groups):
            if not getattr(ntree, "is_sn", False):
                flt_flags[i] = 0

        return flt_flags, flt_neworder
