import bpy


def get_selected_graph():
    sn = bpy.context.scene.sn
    if sn.node_tree_index < len(bpy.data.node_groups):
        ntree = bpy.data.node_groups[sn.node_tree_index]
        if ntree.bl_idname == "ScriptingNodesTree":
            cat_list = list(map(lambda cat: cat.name, sn.graph_categories))

            if sn.active_graph_category == "ALL":
                return ntree
            elif sn.active_graph_category == "OTHER":
                if ntree.category == "OTHER" or not ntree.category or not ntree.category in cat_list:
                    return ntree
            elif ntree.category == sn.active_graph_category:
                return ntree
    return None

def get_filtered_graphs():
    filtered = []
    sn = bpy.context.scene.sn
    for ntree in bpy.data.node_groups:
        if ntree.bl_idname == "ScriptingNodesTree":
            cat_list = list(map(lambda cat: cat.name, sn.graph_categories))
            if sn.active_graph_category == "ALL":
                filtered.append(ntree)
            elif sn.active_graph_category == "OTHER":
                if ntree.category == "OTHER" or not ntree.category or not ntree.category in cat_list:
                    filtered.append(ntree)
            elif ntree.category == sn.active_graph_category:
                filtered.append(ntree)
                
    filtered = list(sorted(filtered, key=lambda n: n.index))
    return filtered

def get_selected_graph_offset(offset):
    selected = get_selected_graph()
    filtered = get_filtered_graphs()
    if selected:
        i = filtered.index(selected)
        i += offset
        if i >= 0 and i < len(filtered):
            return filtered[i]
    return None



class SN_UL_GraphList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon="SCRIPT")
        row.prop(item, "name", emboss=False, text="")
        if context.scene.sn.show_graph_categories:
            row.operator("sn.move_graph_category", text="", icon="FORWARD", emboss=False).index = index

    def filter_items(self, context, data, propname):
        sn = context.scene.sn
        node_trees = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        _sort = [(idx, frame) for idx, frame in enumerate(bpy.data.node_groups)]
        flt_neworder = helper_funcs.sort_items_helper(_sort, lambda e: getattr(e[1], "index", 0), False)
        
        if sn.active_graph_category == "ALL":
            flt_flags = helper_funcs.filter_items_by_name("ScriptingNodesTree", self.bitflag_filter_item, node_trees, "bl_idname", reverse=False)
            return flt_flags, flt_neworder
        
        elif sn.active_graph_category == "OTHER":
            flt_flags = []
            cat_list = list(map(lambda cat: cat.name, sn.graph_categories))
            for tree in node_trees:
                if not hasattr(tree, "category"):
                    flt_flags.append(0)
                elif tree.category == "OTHER" or not tree.category or not tree.category in cat_list:
                    flt_flags.append(self.bitflag_filter_item)
                else:
                    flt_flags.append(0)
            return flt_flags, flt_neworder
        
        else:
            flt_flags = []
            for tree in node_trees:
                if not hasattr(tree, "category"):
                    flt_flags.append(0)
                elif tree.category == sn.active_graph_category:
                    flt_flags.append(self.bitflag_filter_item)
                else:
                    flt_flags.append(0)
            return flt_flags, flt_neworder
