import bpy


def update_graph_index(self, context):
    graph_tree = self.sn_graphs[self.sn_graph_index].node_tree
    context.space_data.node_tree = graph_tree
    context.scene.sn.bookmarks = self.sn_graphs[self.sn_graph_index].name


def name_is_unique(collection, name):
    count = 0
    for item in collection:
        if item.name == name:
            count += 1
    return count <= 1

def get_unique_name(collection, base_name):
    if name_is_unique(collection, base_name):
        return base_name
    else:
        max_num = 0
        if "." in base_name and base_name.split(".")[-1].isnumeric():
            base_name = (".").join(base_name.split(".")[:-1])
        for item in collection:
            if "." in item.name and item.name.split(".")[-1].isnumeric():
                item_base_name = (".").join(item.name.split(".")[:-1])
                if item_base_name == base_name:
                    max_num = max(max_num, int(item.name.split(".")[-1]))
        return base_name + "." + str(max_num+1).zfill(3)


class SN_Graph(bpy.types.PropertyGroup):

    def update_name(self,context):
        unique_name = get_unique_name(self.main_tree.sn_graphs, self.name)
        if not self.name == unique_name:
            self.name = unique_name
        self.node_tree.name = self.name

    main_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)

    node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)
    
    name: bpy.props.StringProperty(name="Name", description="The name of this graph", default="My Graph", update=update_name)

    bookmarked: bpy.props.BoolProperty(default=False,name="Bookmark",description="Will show this graph in the header for quick access")


class SN_UL_GraphList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon="FILE_SCRIPT" if index==0 else "SCRIPT")
        row.label(text=item.name)
        row.prop(item, "bookmarked", icon="BOOKMARKS" if item.bookmarked else "BLANK1", text="", emboss=False)