from ....lib.utils.is_sn import is_sn
import bpy


class SNA_UL_NodeTreesList(bpy.types.UIList):
    """Lists addon-level node trees. Group/function trees are hidden -
    they're shown in the Functions sub-panel instead."""

    bl_idname = "SNA_UL_NodeTreesList"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        layout.prop(item, "name", text="", emboss=False)

    def filter_items(self, context, data, propname):
        groups = bpy.data.node_groups
        helper_funcs = bpy.types.UI_UL_list
        flt_neworder = []

        # Filtering by name (if user typed a filter)
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(
                self.filter_name,
                self.bitflag_filter_item,
                groups,
                "name",
                reverse=self.use_filter_sort_reverse,
            )
        if not self.filter_name or not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(groups)

        # Hide non-SN trees and group/function trees
        for i, ntree in enumerate(groups):
            if not is_sn(ntree) or getattr(ntree, "is_group", False):
                flt_flags[i] = 0

        return flt_flags, flt_neworder
