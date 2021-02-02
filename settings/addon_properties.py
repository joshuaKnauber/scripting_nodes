import os
import bpy
import json
from ..node_tree.base_node import SN_NodeCollection


example_dict = {
    "Functions": {
        "tree_name": "Functions",
        "icon": "HANDLETYPE_FREE_VEC"
    },
    "Operator": {
        "tree_name": "Operator",
        "icon": "SEQ_CHROMA_SCOPE"
    },
    "Events / Program": {
        "tree_name": "Events / Program",
        "icon": "ARMATURE_DATA"
    },
    "Interface": {
        "tree_name": "Interface",
        "icon": "RESTRICT_VIEW_ON"
    },
    "Blend Data": {
        "tree_name": "Blend Data",
        "icon": "MONKEY"
    },
    "Variables": {
        "tree_name": "Variables",
        "icon": "DRIVER_TRANSFORM"
    },
    "Properties": {
        "tree_name": "Properties",
        "icon": "MOD_SOFT"
    },
    # "Run Function On": {
    #     "tree_name": "Run Function On",
    #     "icon": "MOD_SCREW"
    # },
    "Interface Function": {
        "tree_name": "Interface Function",
        "icon": "RESTRICT_VIEW_OFF"
    },
}


class SN_PackageDisplay(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    price: bpy.props.StringProperty()
    url: bpy.props.StringProperty()
    author: bpy.props.StringProperty()



class SN_AddonDisplay(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    category: bpy.props.StringProperty()
    author: bpy.props.StringProperty()
    price: bpy.props.StringProperty()
    blender_version: bpy.props.IntVectorProperty()
    addon_version: bpy.props.IntVectorProperty()

    has_blend: bpy.props.BoolProperty()
    is_external: bpy.props.BoolProperty()

    addon_url: bpy.props.StringProperty()
    blend_url: bpy.props.StringProperty()
    
    show_addon: bpy.props.BoolProperty(default=False)



class SN_AddonProperties(bpy.types.PropertyGroup):


    def addon_tree(self):
        for tree in bpy.data.node_groups:
            if len(tree.sn_graphs) and tree.sn_graphs[0].name == self.editing_addon:
                return tree


    def active_addon_has_changes(self):
        for graph in self.addon_tree().sn_graphs:
            if graph.node_tree.has_changes:
                return True
        return False


    def get_addon_items(self,context):
        items = []
        for tree in bpy.data.node_groups:
            if len(tree.sn_graphs):
                items.append((tree.sn_graphs[0].name,tree.sn_graphs[0].name,tree.sn_graphs[0].name))
        if items:
            return items
        return [("NONE","NONE","NONE")]


    def update_editing_addon(self,context):
        addon_tree = self.addon_tree()
        addon_tree.sn_graph_index = addon_tree.sn_graph_index


    def get_example_items(self, context):
        global example_dict
        example_list = []
        for index, key in enumerate(example_dict):
            example = example_dict[key]
            example_list.append((key,key,key,example["icon"],index+1))

        return [("NONE", "Examples", "Choose an example", "PRESET", 0)] + example_list

    def update_examples(self, context):
        if self.example_dropdown != "NONE":
            with bpy.data.libraries.load(os.path.join(os.path.dirname(os.path.dirname(__file__)),"examples.blend")) as (data_from, data_to):
                data_to.node_groups = [self.example_dropdown]

            context.scene.sn.editing_addon = self.example_dropdown
            bpy.ops.sn.compile()
            self.example_dropdown = "NONE"


    editing_addon: bpy.props.EnumProperty(items=get_addon_items,
                                        update=update_editing_addon,
                                        name="Editing Addon",
                                        description="Select the addon you want to edit")

    example_dropdown: bpy.props.EnumProperty(items=get_example_items,
                                        update=update_examples,
                                        name="Examples",
                                        description="Select the example you want to see")


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
    
    
    show_char_control: bpy.props.BoolProperty(default=False,
                                              name="Show Line Wrap",
                                              description="Shows the control for line wrapping")
    
    
    chars_per_line: bpy.props.IntProperty(default=10,
                                          min=5,
                                          max=50,
                                          name="Line Wrap",
                                          description="Amount of characters which should go in one line")


    ttp_addon_info: bpy.props.BoolProperty(default=True,
                                           name="Addon Info",
                                           description="This is the information that will be displayed in the user preferences")
    
    
    packages: bpy.props.CollectionProperty(type=SN_PackageDisplay)
    addons: bpy.props.CollectionProperty(type=SN_AddonDisplay)
    
    
    sn_compat_nodes: bpy.props.CollectionProperty(type=SN_NodeCollection,name="Suggestion Menu")
    
    
    minimal_header: bpy.props.BoolProperty(default=False,name="Minimal Header",
                                         description="Only show a minimal header")