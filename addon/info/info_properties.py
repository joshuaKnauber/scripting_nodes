import bpy

from ...core.builder import builder

from .names_generator import generate_name


def reset_addon_info_has_changes():
    bpy.context.scene.sna.info.has_changes = False


def initialize_addon_info():
    sna = bpy.context.scene.sna
    if not sna.info.initialized:
        sna.info.name = generate_name(style="capital") + " Addon"
        sna.info.initialized = True


class SNA_AddonInfoProperties(bpy.types.PropertyGroup):
    def update_changes(self, context):
        self.has_changes = True

    has_changes: bpy.props.BoolProperty(default=False)

    initialized: bpy.props.BoolProperty(default=False)

    name: bpy.props.StringProperty(
        default="New Addon",
        name="Name",
        description="The name of the addon",
        update=update_changes,
    )

    description: bpy.props.StringProperty(
        default="",
        name="Description",
        description="The description of the addon",
        update=update_changes,
    )

    author: bpy.props.StringProperty(
        default="Your Name",
        name="Author",
        description="The author of this addon",
        update=update_changes,
    )

    version: bpy.props.IntVectorProperty(
        default=(1, 0, 0),
        size=3,
        min=0,
        name="Version",
        description="The version of the addon",
        update=update_changes,
    )

    blender: bpy.props.IntVectorProperty(
        default=(4, 0, 0),
        size=3,
        min=0,
        name="Minimum Blender",
        description="Minimum blender version required for this addon",
        update=update_changes,
    )

    location: bpy.props.StringProperty(
        default="",
        name="Location",
        description="Describes where the addons functionality can be found",
        update=update_changes,
    )

    warning: bpy.props.StringProperty(
        default="",
        name="Warning",
        description="Warning if there is a bug or a problem that the user should be aware of",
        update=update_changes,
    )

    doc_url: bpy.props.StringProperty(
        default="",
        name="Doc URL",
        description="URL to the addons documentation",
        update=update_changes,
    )

    tracker_url: bpy.props.StringProperty(
        default="",
        name="Tracker URL",
        description="URL to the addons bug tracker",
        update=update_changes,
    )

    def get_categories(self, context):
        categories = [
            "3D View",
            "Add Mesh",
            "Add Curve",
            "Animation",
            "Compositing",
            "Development",
            None,
            "Game Engine",
            "Import-Export",
            "Lighting",
            "Material",
            "Mesh",
            "Node",
            None,
            "Object",
            "Paint",
            "Physics",
            "Render",
            "Rigging",
            "Scene",
            None,
            "Sequencer",
            "System",
            "Text Editor",
            "UV",
            "User Interface",
        ]
        items = []
        for cat in categories:
            if cat:
                items.append((cat, cat, cat))
            else:
                items.append(("", "", ""))
        return items + [("CUSTOM", "- Custom Category -", "Add your own category")]

    category: bpy.props.EnumProperty(
        items=get_categories,
        name="Category",
        description="The preferences category the addon will be displayed in",
        update=update_changes,
    )

    custom_category: bpy.props.StringProperty(
        default="My Category",
        name="Custom Category",
        description="Your custom category",
        update=update_changes,
    )

    @property
    def module_name(self):
        if self.use_custom_module_name:
            return self.custom_module_name
        return self.name.lower().replace(" ", "_")

    use_custom_module_name: bpy.props.BoolProperty(
        default=False,
        name="Use Custom Identifier",
        description="Use a custom identifier for the addon",
        update=update_changes,
    )

    custom_module_name: bpy.props.StringProperty(
        default="new_addon",
        name="Addon Identifier",
        description="The identifier of the addon",
        update=update_changes,
    )

    use_custom_shorthand: bpy.props.BoolProperty(
        default=False,
        name="Use Custom Shorthand",
        description="Use a custom shorthand for the addon",
        update=update_changes,
    )

    shorthand: bpy.props.StringProperty(
        default="SNA",
        name="Addon Shorthand",
        description="The shorthand of the addon",
        update=update_changes,
    )

    persist_sessions: bpy.props.BoolProperty(
        default=False,
        name="Persist Addon",
        description="Keep the addon installed across blender sessions. This is only relevant during development",
    )
