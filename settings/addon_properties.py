import bpy
import os



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