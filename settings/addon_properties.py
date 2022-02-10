import bpy
from bl_ui import space_userpref
from uuid import uuid4

from .data_properties import SN_DataProperty, is_valid_attribute
from ..addon.properties.properties import SN_GeneralProperties
from ..addon.properties.settings.settings import property_icons
from ..addon.assets.assets import SN_AssetProperties
from ..utils import get_python_name
            


class SN_AddonProperties(bpy.types.PropertyGroup):

    # stores the unregister functions for nodes with their memory adress as the key to recall them when reregistering
    unregister_cache = {}


    # stores the preferences draw function while compiling the addon to draw in the serpens preferences
    preferences = []
    
    
    # stores the custom icon property collections while developing an addon
    preview_collections = {}
    
    
    # stores functions that are needed to be stored while developing an addon
    node_function_cache = {}


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
                                        name="Log Code",
                                        description="Prints the code that is being run when a node changes")

    debug_python_properties: bpy.props.BoolProperty(default=False,
                                        name="Debug Properties",
                                        description="Debug internal property code")


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
            # TODO only if node tree in space data
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
    
    
    def create_data_items(self, data, data_path):
        for attr in dir(data):
            if is_valid_attribute(attr):
                prop = None if not hasattr(data, "bl_rna") or not attr in data.bl_rna.properties else data.bl_rna.properties[attr]
                item = self.data_items.add()
                if prop:
                    item.name = prop.name if prop.name else prop.identifier
                    item.description = prop.description if prop.description else item.name
                    item.type = prop.type
                else:
                    item.name = attr
                    item.description = attr
                    item.type = str(type(getattr(data, attr)))
                item.identifier = attr
                item.path = f"{data_path}.{attr}"
                item.parent_path = data_path
                item.has_properties = hasattr(getattr(data, attr), "bl_rna")
    
    def update_data_category(self, context):
        self.data_items.clear()
        self.create_data_items(getattr(bpy, self.data_category), f"bpy.{self.data_category}")

    def update_hide_preferences(self, context):
        for cls in space_userpref.classes:
            try:
                if self.hide_preferences: bpy.utils.unregister_class(cls)
                else: bpy.utils.register_class(cls)
            except: pass
        self.update_data_category(context)
            
    hide_preferences: bpy.props.BoolProperty(default=False,
                                        name="Hide Preferences",
                                        description="Hides all panels in the preferences window",
                                        update=update_hide_preferences)
    
    data_category: bpy.props.EnumProperty(name="Category",
                                        items=[("app", "App", "bpy.app"),
                                               ("context", "Context", "bpy.context"),
                                               ("data", "Data", "bpy.data"),
                                               ("path", "Path", "bpy.path"),
                                               ("utils", "Utils", "bpy.utils")],
                                        default="context",
                                        description="Category of blend data",
                                        update=update_data_category)
    
    data_items: bpy.props.CollectionProperty(type=SN_DataProperty)
    
    data_filter: bpy.props.EnumProperty(name="Type",
                                        options={"ENUM_FLAG"},
                                        description="Filter by data type",
                                        items=[("POINTER", "Pointer", "Pointer", property_icons["Property"], 1),
                                               ("COLLECTION", "Collection", "Collection", property_icons["Collection"], 2),
                                               ("STRING", "String", "String", property_icons["String"], 4),
                                               ("ENUM", "Enum", "Enum", property_icons["Enum"], 8),
                                               ("BOOLEAN", "Boolean", "Boolean", property_icons["Boolean"], 16),
                                               ("INT", "Integer", "Integer", property_icons["Integer"], 32),
                                               ("FLOAT", "Float", "Float", property_icons["Float"], 64)],
                                        default={"POINTER","COLLECTION","STRING","ENUM","BOOLEAN","INT","FLOAT"})