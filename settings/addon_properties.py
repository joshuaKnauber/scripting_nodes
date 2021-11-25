import os
import bpy
import json
from ..node_tree.base_node import SN_NodeCollection
from ..node_tree.graphs.graph_ui_lists import SN_Graph


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
    "Interface Example": {
        "tree_name": "Interface Example",
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


class SN_SnippetDisplay(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    price: bpy.props.StringProperty()
    url: bpy.props.StringProperty()
    blend_url: bpy.props.StringProperty()
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

    def update_editing_addon(self, context):
        addon_tree = self.addon_tree()
        addon_tree.sn_graph_index = addon_tree.sn_graph_index

    def get_example_items(self, context):
        global example_dict
        example_list = []
        for index, key in enumerate(example_dict):
            example = example_dict[key]
            example_list.append((key, key, key, example["icon"], index+1))

        return [("NONE", "Examples", "Choose an example", "PRESET", 0)] + example_list

    def update_examples(self, context):
        if self.example_dropdown != "NONE":
            with bpy.data.libraries.load(os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples.blend")) as (data_from, data_to):
                data_to.node_groups = [self.example_dropdown]

            context.scene.sn.editing_addon = self.example_dropdown
            bpy.ops.sn.compile()
            self.example_dropdown = "NONE"

    example_dropdown: bpy.props.EnumProperty(items=get_example_items,
                                             update=update_examples,
                                             name="Examples",
                                             description="Select the example you want to see")

    def get_bookmarked_items(self, context):
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
            full_items.append((item, item, item, "SCRIPT", len(full_items)))

        return full_items

    def update_select_bookmarked(self, context):
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
    snippets: bpy.props.CollectionProperty(type=SN_SnippetDisplay)

    sn_compat_nodes: bpy.props.CollectionProperty(
        type=SN_NodeCollection, name="Suggestion Menu")

    snippet_categories: bpy.props.CollectionProperty(
        type=SN_NodeCollection, name="Installed Snippet Categories")

    has_other_snippets: bpy.props.BoolProperty(
        default=False, name="Other snippets installed")

    minimal_header: bpy.props.BoolProperty(default=False, name="Minimal Header",
                                           description="Only show a minimal header")

    insert_sockets: bpy.props.BoolProperty(default=False, name="Show Insert Sockets",
                                           description="Shows add icons on removable sockets to allow inserting sockets")

    python_buttons: bpy.props.BoolProperty(default=False, name="Show Copy Python Buttons",
                                           description="Shows copy python buttons on some sockets and on properties/variables")

    use_autosave: bpy.props.BoolProperty(
        default=False, name="Auto Save", description="Save this file automatically")

    autosave_delay: bpy.props.FloatProperty(
        default=120, name="Delay", description="Autosave delay in seconds", min=10)

    has_update: bpy.props.BoolProperty(default=False)

    easy_bpy: bpy.props.PointerProperty(type=bpy.types.Text, name="EasyBPY",
                                        description="The easy bpy text file for using easy bpy in your scripts")




    node_tree_index: bpy.props.IntProperty(default=0, name="Active Node Tree", description="The node tree you're currently editing")

    addon_name: bpy.props.StringProperty(default="My Addon",
                                        name="Addon Name",
                                        description="The name of the addon")

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
        self.update_changes(context)

    blender: bpy.props.IntVectorProperty(default=(3, 0, 0),
                                        update=update_blender,
                                        size=3,
                                        min=0,
                                        name="Minimum Blender",
                                        description="Minimum blender version required for this addon")

    location: bpy.props.StringProperty(default="",
                                        name="Location",
                                        description="Describes where the addons functionality can be found")

    warning: bpy.props.StringProperty(default="",
                                        name="Warning",
                                        description="Used if there is a bug or a problem that the user should be aware of")

    doc_url: bpy.props.StringProperty(default="",
                                        name="Doc URL",
                                        description="URL to the addons documentation")

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
        return items+[("CUSTOM","- Custom Category -","Add your own category")]

    category: bpy.props.EnumProperty(items=get_categories,
                                        name="Category",
                                        description="The category the addon will be displayed in")

    custom_category: bpy.props.StringProperty(default="My Category",
                                        name="Custom Category",
                                        description="Your custom category")