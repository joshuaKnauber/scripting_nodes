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
    
    name: bpy.props.StringProperty(name="Name", description="The name of this graph or the addon", default="My Graph", update=update_name)

    main_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)

    node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)

    bookmarked: bpy.props.BoolProperty(default=False,
                                        name="Bookmark",
                                        description="Will show this graph in the header for quick access")

    description: bpy.props.StringProperty(default="",
                                        name="Description",
                                        description="The description of the addon")

    author: bpy.props.StringProperty(default="Your Name",
                                        name="Author",
                                        description="The author of this addon")

    version: bpy.props.IntVectorProperty(default=(1,0,0),
                                        size=3,
                                        min=0,
                                        name="Version",
                                        description="The author of this addon")

    def update_blender(self,context):
        if not self.blender[1] > 9:
            self.blender = (self.blender[0],int(str(self.blender[1])+"0"),self.blender[2])

    blender: bpy.props.IntVectorProperty(default=(2,80,0),
                                        update=update_blender,
                                        size=3,
                                        min=0,
                                        name="Blender",
                                        description="Minimum blender version required for this addon")

    location: bpy.props.StringProperty(default="",
                                        name="Location",
                                        description="Describes where the addons functionality can be found")

    warning: bpy.props.StringProperty(default="",
                                        name="Warning",
                                        description="Used if there is a bug or a problem that the user should be aware of")

    wiki_url: bpy.props.StringProperty(default="",
                                        name="Wiki URL",
                                        description="URL to the addons wiki")

    tracker_url: bpy.props.StringProperty(default="",
                                        name="Tracker URL",
                                        description="URL to the addons bug tracker")

    def get_categories(self,context):
        categories = ["3D View", "Add Mesh", "Add Curve", "Animation", "Compositing", "Development", None,
                    "Game Engine", "Import-Export", "Lighting", "Material","Mesh","Node",None,
                    "Object","Paint","Physics","Render","Rigging","Scene",None,
                    "Sequencer","System","Text Editor","UV","User Interface"]
        items = []
        for cat in categories:
            if cat:
                items.append((cat,cat,cat))
            else:
                items.append(("","",""))
        return items+[("CUSTOM","Custom","Add your own category")]

    category: bpy.props.EnumProperty(items=get_categories,
                                        name="Category",
                                        description="The category the addon will be displayed in")

    custom_category: bpy.props.StringProperty(default="My Category",
                                        name="Custom Category",
                                        description="Your custom category")



class SN_UL_GraphList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon="FILE_SCRIPT" if index==0 else "SCRIPT")
        row.label(text=item.name)
        row.prop(item, "bookmarked", icon="BOOKMARKS" if item.bookmarked else "BLANK1", text="", emboss=False)