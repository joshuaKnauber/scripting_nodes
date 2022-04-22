import bpy
from bl_ui import space_userpref
from uuid import uuid4


from .data_properties import get_data_items, filter_items, filter_defaults
from ..addon.properties.properties import SN_GeneralProperties
from ..addon.assets.assets import SN_AssetProperties
from ..utils import get_python_name
from .load_markets import SN_Addon, SN_Package, SN_Snippet
from ..packages.snippet_ops import SN_SnippetCategory
            


class SN_AddonProperties(bpy.types.PropertyGroup):
    
    # stores the unregister function for the addon when its compiled
    addon_unregister = []


    # stores the preferences draw function while compiling the addon to draw in the serpens preferences
    preferences = []
    
    
    # stores the custom icon property collections while developing an addon
    preview_collections = {}
    
    
    compile_time: bpy.props.FloatProperty(name="Compile Time",
                                        description="Time the addon took to compile")


    @property
    def module_name(self):
        return get_python_name(bpy.context.scene.sn.addon_name, replacement=f"addon_{uuid4().hex[:5].upper()}")


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


    format_code: bpy.props.BoolProperty(default=False,
                                        name="Format Code",
                                        description="This will format the code during debugging")

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
    
    
    data_items = {"app": {}, "context": {}, "data": {},}# "path": {}, "utils": {}}
        
    def reload_data_category(self, category):
        """ Reloads the basic data for a category """
        if category != "context":
            self.data_items[category] = get_data_items(f"bpy.{category}", getattr(bpy, category))
        else:
            ctxt = self.copied_context[0] if self.copied_context else bpy.context.copy()
            self.data_items[category] = get_data_items(f"bpy.context", ctxt)

    def load_categories(self):
        """ Loads the data for the bpy categories """
        self.reload_data_category("app")
        self.reload_data_category("context")
        self.reload_data_category("data")
        # self.reload_data_category("path")
        # self.reload_data_category("utils")

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

    def get_categories(self, context):
        ctxt = "Nothing Copied"
        if context.scene.sn.copied_context:
            ctxt = f"{self.copied_context[0]['area'].type.replace('_', ' ').title()} {self.copied_context[0]['region'].type.replace('_', ' ').title()}"
        items = [("app", "App", "bpy.app"),
                ("context", f"Context ({ctxt})", "bpy.context"),
                ("data", "Data", "bpy.data")]
        return items
    
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
                                        options={"TEXTEDIT_UPDATE"})
    
    show_path: bpy.props.BoolProperty(name="Show Path",
                                        description="Show python path of properties",
                                        default=False)
    
    
    addons: bpy.props.CollectionProperty(type=SN_Addon)

    packages: bpy.props.CollectionProperty(type=SN_Package)

    snippets: bpy.props.CollectionProperty(type=SN_Snippet)
    
    snippet_categories: bpy.props.CollectionProperty(type=SN_SnippetCategory)