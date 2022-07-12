import bpy
from bl_ui import space_userpref
from uuid import uuid4



from .data_properties import get_data_items, filter_items, filter_defaults
from .handle_script_changes import unwatch_script_changes, watch_script_changes
from ..addon.properties.properties import SN_GeneralProperties
from ..addon.properties.property_category import SN_PropertyCategory
from ..node_tree.graphs.graph_category_ops import SN_GraphCategory
from ..addon.assets.assets import SN_AssetProperties
from ..utils import get_python_name
from .load_markets import SN_Addon, SN_Package, SN_Snippet
from ..extensions.snippet_ops import SN_BoolCollection, SN_SnippetCategory
from ..nodes.compiler import compile_addon
            


_item_map = dict()

class SN_AddonProperties(bpy.types.PropertyGroup):
    
    # stores the unregister function for the addon when its compiled
    addon_unregister = []


    # stores the preferences draw function while compiling the addon to draw in the serpens preferences
    preferences = []
    
    
    # stores the custom icon property collections while developing an addon
    preview_collections = {}
    
    
    # stores functions that need to be called during developement
    function_store = {}
    
    
    compile_time: bpy.props.FloatProperty(name="Compile Time",
                                        description="Time the addon took to compile")


    @property
    def module_name(self):
        return get_python_name(bpy.context.scene.sn.addon_name, replacement=f"addon_{uuid4().hex[:5].upper()}")
    
    
    def update_reregister(self, context):
        if not self.pause_reregister:
            compile_addon()
            
    pause_reregister: bpy.props.BoolProperty(default=False,
                                        name="Pause Reregistering",
                                        description="Pauses reregistering the addon when changes are made",
                                        update=update_reregister)


    snippet_vars_customizable: bpy.props.CollectionProperty(type=SN_BoolCollection,
                                        name="Variables Customizable",
                                        description="Saves customizable setting of snippet variables")


    snippet_props_customizable: bpy.props.CollectionProperty(type=SN_BoolCollection,
                                        name="Properties Customizable",
                                        description="Saves customizable setting of snippet properties")


    is_exporting: bpy.props.BoolProperty(default=False,
                                        name="Is Exporting",
                                        description="Saves the current status of exporting to evaluate nodes differently")


    picker_active: bpy.props.BoolProperty(default=False,
                                        name="Picker Is Active",
                                        description="This is enabled when a location picker for panels or similar is active")
    
    
    last_copied_datatype: bpy.props.StringProperty(default="",
                                        name="Last Copied Data Type",
                                        description="The type of data last copied with the copy property button")
                                        
    last_copied_datapath: bpy.props.StringProperty(default="",
                                        name="Last Copied Data Path",
                                        description="The path of data last copied with the copy property button")
                                        
    last_copied_required: bpy.props.StringProperty(default="",
                                        name="Last Copied Required Properties",
                                        description="The identifiers of the last copied required properties separated by ;")
                                        
    copied_context = []


    show_wrap_settings: bpy.props.BoolProperty(default=False,
                                        name="Show Wrap Settings",
                                        description="If this is enabled, the wrapping settings for the text in these panels are show.")

    line_length: bpy.props.IntProperty(default=40, min=10,
                                        name="Line Wrap",
                                        description="The amount of characters shown in a single line in the panel.")


    has_update: bpy.props.BoolProperty(name="Has Update",
                                        description="If Serpens has an available update or not. This is set on file load.",
                                        default=False)


    debug_python_nodes: bpy.props.BoolProperty(default=False,
                                        name="Debug Nodes",
                                        description="Debug internal node code")

    debug_python_sockets: bpy.props.BoolProperty(default=False,
                                        name="Debug Sockets",
                                        description="Debug internal socket code")

    debug_code: bpy.props.BoolProperty(default=False,
                                        name="Keep Code",
                                        description="Keeps a python file in the text editor when the code changes")

    debug_python_properties: bpy.props.BoolProperty(default=False,
                                        name="Debug Properties",
                                        description="Debug internal property code")

    debug_compile_time: bpy.props.BoolProperty(default=False,
                                        name="Debug Compile Time",
                                        description="Prints the time it takes to compile the code")


    insert_sockets: bpy.props.BoolProperty(default=False,
                                        name="Insert Socket Buttons",
                                        description="Show an insert button on dynamic sockets to insert a new socket above")


    compile_on_load: bpy.props.BoolProperty(default=True,
                                        name="Compile On Load",
                                        description="Compile this addon when the file is loaded")


    easy_bpy_path: bpy.props.StringProperty(default="",
                                        name="Easy BPY Path",
                                        description="Gets set when a file is loaded. Set to the easy bpy file path.")


    def update_node_tree_index(self, context):
        if len(bpy.data.node_groups):
            if hasattr(bpy.context.space_data, "node_tree"):
                bpy.context.space_data.node_tree = bpy.data.node_groups[self.node_tree_index]

    node_tree_index: bpy.props.IntProperty(default=0, min=0, name="Active Node Tree", description="The node tree you're currently editing", update=update_node_tree_index)


    properties: bpy.props.CollectionProperty(type=SN_GeneralProperties)

    property_index: bpy.props.IntProperty(default=0, min=0, name="Active Property", description="The property you're currently editing")

    def update_show_property_categories(self, context):
        self.active_prop_category = "ALL"

    show_property_categories: bpy.props.BoolProperty(name="Show Property Categories",
                                        description="Show categories for your addon properties",
                                        default=False, update=update_show_property_categories)

    property_categories: bpy.props.CollectionProperty(type=SN_PropertyCategory)

    def prop_category_items(self, context):
        cat_list = list(map(lambda cat: cat.name, self.property_categories))
        no_cat = 0
        for prop in self.properties:
            if not prop.category or prop.category == "OTHER" or not prop.category in cat_list:
                no_cat += 1

        items = [("ALL", f"All Properties ({len(self.properties)})", "Show all properties"),
                ("OTHER", f"Uncategorized Properties ({no_cat})", "Properties without a category")]

        for item in self.property_categories:
            amount = 0
            for prop in self.properties:
                if prop.category and prop.category == item.name:
                    amount += 1
            items.append((item.name if item.name else "-", f"{item.name} ({amount})", item.name))
        return items
    
    active_prop_category: bpy.props.EnumProperty(name="Category",
                                        description="The properties shown",
                                        items=prop_category_items)


    assets: bpy.props.CollectionProperty(type=SN_AssetProperties)

    asset_index: bpy.props.IntProperty(default=0, min=0, name="Active Asset", description="The asset you're currently editing")


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

    blender: bpy.props.IntVectorProperty(default=(3, 0, 0),
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
    
    
    data_items = { "app": {}, "context": {}, "data": {} }
    ops_items = { "operators": {}, "filtered": {} }
    
    def overwrite_data_items(self, data):
        self.data_items["data"] = data["data"]
        self.data_items["context"] = data["context"]
        self.data_items["app"] = data["app"]
        
    def reload_data_category(self, category):
        """ Reloads the basic data for a category """
        if category != "context":
            self.data_items[category] = get_data_items(f"bpy.{category}", getattr(bpy, category))
        else:
            ctxt = self.copied_context[0] if self.copied_context else bpy.context.copy()
            self.data_items[category] = get_data_items(f"bpy.context", ctxt)

    def refresh_filtered_ops(self):
        """ Sets the filtered operators """
        filtered = {}
        for cat in self.ops_items["operators"]:
            cat_ops = []
            for op in self.ops_items["operators"][cat]["items"]:
                if self.data_search.lower() in op["name"].lower() or self.data_search.lower() in op["operator"].lower():
                    cat_ops.append(op["operator"])
            if cat_ops:
                filtered[cat] = cat_ops
        self.ops_items["filtered"] = filtered

    def get_category_ops(self, category, cat_name):
        """ Gets the operators for a category """
        ops = []
        for op_name in dir(category):
            if op_name[0].isalpha():
                try: op = eval(f"bpy.ops.{cat_name}.{op_name}")
                except: op = None
                if op:
                    rna = op.get_rna_type()
                    ops.append({
                        "name": getattr(rna, "name", op_name),
                        "operator": op_name,
                    })
        return ops

    def load_operators(self):
        """ Reloads the list of operators """
        self.ops_items["operators"] = {}
        for cat_name in dir(bpy.ops):
            if cat_name[0].isalpha() and not cat_name == "class":
                try: cat = eval(f"bpy.ops.{cat_name}")
                except: cat = None
                if cat:
                    self.ops_items["operators"][cat_name] = {
                        "expanded": False,
                        "items": self.get_category_ops(cat, cat_name)
                    }
        self.refresh_filtered_ops()

    def load_categories(self):
        """ Loads the data for the bpy categories """
        self.reload_data_category("app")
        self.reload_data_category("context")
        self.reload_data_category("data")
        self.load_operators()

    def update_hide_preferences(self, context):
        for cls in space_userpref.classes:
            try:
                if self.hide_preferences: bpy.utils.unregister_class(cls)
                else: bpy.utils.register_class(cls)
            except: pass
        if self.hide_preferences:
            self.load_categories()
            
    hide_preferences: bpy.props.BoolProperty(default=False,
                                        name="Hide Preferences",
                                        description="Hides all panels in the preferences window",
                                        update=update_hide_preferences)
            
    global_search_active: bpy.props.BoolProperty(default=False,
                                        name="Global Search",
                                        description="If the global search is active")
    
    def make_enum_item(self, _id, name, descr, preview_id, uid):
        lookup = str(_id)+"\\0"+str(name)+"\\0"+str(descr)+"\\0"+str(preview_id)+"\\0"+str(uid)
        if not lookup in _item_map:
            _item_map[lookup] = (_id, name, descr, preview_id, uid)
        return _item_map[lookup]

    def get_categories(self, context):
        ctxt = "Preferences"
        if context.scene.sn.copied_context:
            ctxt = f"{self.copied_context[0]['area'].type.replace('_', ' ').title()} {self.copied_context[0]['region'].type.replace('_', ' ').title()}"
        items = [self.make_enum_item("app", "App", "bpy.app", 0, 0),
                self.make_enum_item("context", f"Context ({ctxt})", "bpy.context", 0, 1),
                self.make_enum_item("data", "Data", "bpy.data", 0, 2),
                self.make_enum_item("ops", "Operators", "bpy.ops", 0, 3)]
        return items

    def update_data_search(self, context):
        self.refresh_filtered_ops()
    
    data_category: bpy.props.EnumProperty(name="Category",
                                        items=get_categories,
                                        description="Category of blend data")
    
    data_filter: bpy.props.EnumProperty(name="Type",
                                        options={"ENUM_FLAG"},
                                        description="Filter by data type",
                                        items=filter_items,
                                        default=filter_defaults)

    data_search: bpy.props.StringProperty(name="Search",
                                        description="Search data",
                                        options={"TEXTEDIT_UPDATE"},
                                        update=update_data_search)
    
    show_path: bpy.props.BoolProperty(name="Show Path",
                                        description="Show python path of properties",
                                        default=False)
    
    
    addons: bpy.props.CollectionProperty(type=SN_Addon)

    packages: bpy.props.CollectionProperty(type=SN_Package)

    snippets: bpy.props.CollectionProperty(type=SN_Snippet)
    
    snippet_categories: bpy.props.CollectionProperty(type=SN_SnippetCategory)
    
    
    def update_show_graph_categories(self, context):
        self.active_graph_category = "ALL"
        
    show_graph_categories: bpy.props.BoolProperty(name="Show Graph Categories",
                                        description="Show categories for your addon graphs",
                                        default=False, update=update_show_graph_categories)

    graph_categories: bpy.props.CollectionProperty(type=SN_GraphCategory)

    def graph_category_items(self, context):
        cat_list = list(map(lambda cat: cat.name, self.graph_categories))
        no_cat = 0
        ntree_amount = 0
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                ntree_amount += 1
                if not ntree.category or ntree.category == "OTHER" or not ntree.category in cat_list:
                    no_cat += 1

        items = [("ALL", f"All Graphs ({ntree_amount})", "Show all graphs"),
                ("OTHER", f"Uncategorized Graphs ({no_cat})", "Graphs without a category")]

        for item in self.graph_categories:
            amount = 0
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    if ntree.category and ntree.category == item.name:
                        amount += 1
            items.append((item.name if item.name else "-", f"{item.name} ({amount})", item.name))
        return items
    
    active_graph_category: bpy.props.EnumProperty(name="Category",
                                        description="The graphs shown",
                                        items=graph_category_items)
    
    
    overwrite_variable_graph: bpy.props.BoolProperty(name="Overwrite Variable Graph",
                                        description="Let's you pick a graph to show the variable list from",
                                        default=False)

    def get_variable_graph_items(self, context):
        items = []
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                items.append((ntree.name, ntree.name, ntree.name))
        return items
    
    variable_graph: bpy.props.EnumProperty(name="Variable Graph",
                                        description="Graph to display variables from",
                                        items=get_variable_graph_items)
    
    
    remove_duplicate_code: bpy.props.BoolProperty(name="Remove Duplicate Code",
                                        description="Removes duplicate code in the generated code (small performance impact for large addons)",
                                        default=True)
    
    format_code: bpy.props.BoolProperty(name="Format Code",
                                        description="Formats linebreaks in the generated code (small performance impact for large addons)",
                                        default=True)
    
    
    def update_watch_scripts(self, context):
        if self.watch_script_changes:
            watch_script_changes()
        else:
            unwatch_script_changes()
    
    watch_script_changes: bpy.props.BoolProperty(name="Watch Script Changes",
                                        description="Will watch for changes in the scripts of your run script nodes and recompile the addon when you save the file",
                                        default=False,
                                        update=update_watch_scripts)
    
    multifile: bpy.props.BoolProperty(name="Multifile",
                                        description="Export the separate node trees as separate python files",
                                        default=False)