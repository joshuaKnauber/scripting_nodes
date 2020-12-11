import bpy


class SN_AddonProperties(bpy.types.PropertyGroup):


    def addon_tree(self):
        for tree in bpy.data.node_groups:
            if len(tree.sn_graphs) and tree.sn_graphs[0].name == self.editing_addon:
                return tree


    def get_addon_items(self,context):
        items = []
        for tree in bpy.data.node_groups:
            if len(tree.sn_graphs):
                items.append((tree.sn_graphs[0].name,tree.sn_graphs[0].name,tree.sn_graphs[0].name))
        if items:
            return items
        return [("NONE","NONE","NONE")]

    editing_addon: bpy.props.EnumProperty(items=get_addon_items,
                                        name="Editing Addon",
                                        description="Select the addon you want to edit")


    def get_bookmarked_items(self,context):
        items = []
        addon_tree = context.scene.sn.addon_tree()
        for graph in addon_tree.sn_graphs:
            if graph.bookmarked:
                items.append(graph.name)
        selected_graph = addon_tree.sn_graphs[addon_tree.sn_graph_index]
        selected = selected_graph.name
        if not selected in items:
            items.append(selected)

        full_items = []
        for item in items:
            icon = "FILE_SCRIPT" if item == self.editing_addon else "SCRIPT"
            full_items.append((item,item,item,icon,len(full_items)))
        
        return full_items

    def update_select_bookmarked(self,context):
        addon_tree = context.scene.sn.addon_tree()
        for i, graph in enumerate(addon_tree.sn_graphs):
            if graph.name == self.bookmarks:
                if not addon_tree.sn_graphs[addon_tree.sn_graph_index].name == self.bookmarks:
                    addon_tree.sn_graph_index = i
                    break

    bookmarks: bpy.props.EnumProperty(items=get_bookmarked_items,
                                        update=update_select_bookmarked,
                                        name="Bookmarks",
                                        description="Select a bookmarked graph")


    ttp_addon_info: bpy.props.BoolProperty(default=True,name="Addon Info",description="This is the information that will be displayed in the user preferences")