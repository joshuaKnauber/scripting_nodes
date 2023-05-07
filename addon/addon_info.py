import bpy


class SN_AddonInfoProperties(bpy.types.PropertyGroup):

    addon_name: bpy.props.StringProperty(default="My Addon",
                                         name="Addon Name",
                                         description="The name of the addon")

    description: bpy.props.StringProperty(default="",
                                          name="Description",
                                          description="The description of the addon")

    author: bpy.props.StringProperty(default="Your Name",
                                     name="Author",
                                     description="The author of this addon")

    version: bpy.props.IntVectorProperty(default=(1, 0, 0),
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

    def get_categories(self, context):
        categories = ["3D View", "Add Mesh", "Add Curve", "Animation", "Compositing", "Development", None,
                      "Game Engine", "Import-Export", "Lighting", "Material", "Mesh", "Node", None,
                      "Object", "Paint", "Physics", "Render", "Rigging", "Scene", None,
                      "Sequencer", "System", "Text Editor", "UV", "User Interface"]
        items = []
        for cat in categories:
            if cat:
                items.append((cat, cat, cat))
            else:
                items.append(("", "", ""))
        return items+[("CUSTOM", "- Custom Category -", "Add your own category")]

    category: bpy.props.EnumProperty(items=get_categories,
                                     name="Category",
                                     description="The category the addon will be displayed in")

    custom_category: bpy.props.StringProperty(default="My Category",
                                              name="Custom Category",
                                              description="Your custom category")

    def get_short_identifier(self):
        return self["short_identifier"] if "short_identifier" in self else "sna"

    def set_short_identifier(self, value):
        if not value.strip() or any([not c.isalpha() for c in value]):
            value = "sna"
        self["short_identifier"] = value

    def update_short_identifier(self, context):
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if hasattr(node, "is_root") and node.is_root:
                        ntree.add_to_queue(node)

    short_identifier: bpy.props.StringProperty(
        default="sna", name="Short Identifier", description="Short identifier for the addon used in lower or upper case as an identifier for panels, operators, etc.", get=get_short_identifier, set=set_short_identifier, update=update_short_identifier)
