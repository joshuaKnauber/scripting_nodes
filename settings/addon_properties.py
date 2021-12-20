import bpy
from uuid import uuid4
from ..utils import get_python_name
            


class SN_AddonProperties(bpy.types.PropertyGroup):

    # stores the unregister functions for nodes with their memory adress as the key to recall them when reregistering
    unregister_cache = {}


    # stores the preferences draw function while compiling the addon to draw in the serpens preferences
    preferences = []


    @property
    def module_name(self):
        return get_python_name(bpy.context.scene.sn.addon_name, replacement=f"addon_{uuid4().hex[:5].upper()}")


    is_exporting: bpy.props.BoolProperty(default=False,
                                        name="Is Exporting",
                                        description="Saves the current status of exporting to evaluate nodes differently")


    picker_active: bpy.props.BoolProperty(default=False,
                                        name="Picker Is Active",
                                        description="This is enabled when a location picker for panels or similar is active")


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


    insert_sockets: bpy.props.BoolProperty(default=False,
                                        name="Insert Socket Buttons",
                                        description="Show an insert button on dynamic sockets to insert a new socket above")


    compile_on_load: bpy.props.BoolProperty(default=True,
                                        name="Compile On Load",
                                        description="Compile this addon when the file is loaded")


    easy_bpy: bpy.props.PointerProperty(type=bpy.types.Text,
                                        name="Easy BPY File",
                                        description="The file that contains the easy bpy module")


    def update_node_tree_index(self, context):
        if len(bpy.data.node_groups):
            bpy.context.space_data.node_tree = bpy.data.node_groups[self.node_tree_index]

    node_tree_index: bpy.props.IntProperty(default=0, name="Active Node Tree", description="The node tree you're currently editing", update=update_node_tree_index)


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


    # potential solution for if this https://developer.blender.org/T88986 bug was fixed

    addon_text: bpy.props.PointerProperty(name="Text File",
                                            description="File which the addon is stored in",
                                            type=bpy.types.Text)

    def get_addon_text(self):
        if not self.addon_text:
            self.addon_text = bpy.data.texts.new("Addon File")


"""

any node can have:
- some imperative code
- some imports
- some register code
- some unregister code

are there even trigger nodes?

how do i register and unregister things?
how do nodes that wouldn't be trigger nodes add code?
how would utility functions work if it's not a text file?
how do different node trees work? are there different files? is this different on export?

"""