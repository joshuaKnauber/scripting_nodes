import bpy


class SNA_AddonSettings(bpy.types.PropertyGroup):
    ### General Settings

    addon_name: bpy.props.StringProperty(
        name="Addon Name", description="The name of the addon", default="My Addon"
    )

    ### Build Settings

    is_dirty: bpy.props.BoolProperty(
        default=True,
        name="Is Dirty",
        description="If this is true, the entire addon will be rebuilt including assets and default files",
    )

    module_name_overwrite: bpy.props.StringProperty(
        name="Module Name Overwrite",
        description="An optional name for the folder the addon should be created in",
        default="",
    )

    force_production: bpy.props.BoolProperty(
        name="Force Production",
        description="Force the addon to be built in its production version",
        default=False,
    )

    persist_addon: bpy.props.BoolProperty(
        name="Persist Addon",
        description="Persist the addon when switching files",
        default=False,
    )

    ### Calculated Values

    @property
    def module_name(self):
        return self.module_name_overwrite or self.addon_name
