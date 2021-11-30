import bpy
import os
            


class CodeSnippet:
    """ Represents a part of code in the final file. This handles things like unique function names and is used to get code ready for the python file """

    def __init__(self, code):
        self._code = code

    def update(self, code):
        pass

    @property
    def code(self):
        # handle unique functions names here
        return self._code



class AddonCode:
    """ Represents the final python file with all its code parts. This assembles and updates the python file if necessary """

    def __init__(self):
        self._imports = {}
        self._imperative = {}
        self._register = {}
        self._unregister = {}

    def _save_snippet(self, save_key, key, code, unique_keys):
        if key in getattr(self, save_key):
            getattr(self, save_key)[key].update(code)
        else:
            getattr(self, save_key)[key] = CodeSnippet(code)

    def add_imperative(self, key, code, unique_keys=[]):
        self._save_snippet("_imperative", key, code, unique_keys)



class SN_AddonProperties(bpy.types.PropertyGroup):

    has_update: bpy.props.BoolProperty(name="Has Update",
                                        description="If Serpens has an available update or not. This is set on file load.",
                                        default=False)

    debug_python_nodes: bpy.props.BoolProperty(default=False,
                                        name="Debug Nodes",
                                        description="Debug internal node code")

    debug_python_sockets: bpy.props.BoolProperty(default=False,
                                        name="Debug Sockets",
                                        description="Debug internal socket code")


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