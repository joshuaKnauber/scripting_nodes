import bpy
import re
from uuid import uuid4


def get_short_id():
    """Returns a unique id"""
    return uuid4().hex[:8].upper()


class SNA_AddonSettings(bpy.types.PropertyGroup):

    def update_is_dirty(self, context):
        self.is_dirty = True

    ### General Settings

    addon_name: bpy.props.StringProperty(
        name="Addon Name",
        description="The name of the addon",
        default="My Addon",
        update=update_is_dirty,
    )

    ### Build Settings

    is_exporting: bpy.props.BoolProperty()

    is_dirty: bpy.props.BoolProperty(
        default=True,
        name="Is Dirty",
        description="If this is true, the entire addon will be rebuilt including assets and default files",
    )

    enabled: bpy.props.BoolProperty(
        name="Enabled",
        description="Enable or disable the addon",
        default=True,
        update=update_is_dirty,
    )

    module_name_overwrite: bpy.props.StringProperty(
        name="Module Name",
        description="An optional name for the folder the addon should be created in",
        default="",
        update=update_is_dirty,
    )

    force_production: bpy.props.BoolProperty(
        name="Force Production",
        description="Force the addon to be built in its production version",
        default=False,
        update=update_is_dirty,
    )

    persist_addon: bpy.props.BoolProperty(
        name="Persist Addon",
        description="Persist the addon when switching files",
        default=False,
    )

    addon_uid: bpy.props.StringProperty(
        name="UID",
        description="Unique identifier for this file's addon",
        default="",
    )

    def get_uid(self):
        """Get or generate a unique ID for this file."""
        if not self.addon_uid:
            self.addon_uid = get_short_id()
        return self.addon_uid

    ### Calculated Values

    @property
    def module_name(self):
        return (
            self.module_name_overwrite
            or re.sub(r"[^a-zA-Z\s]", "", self.addon_name).replace(" ", "_").lower()
            or "sna_addon"
        )

    @property
    def build_with_production_code(self):
        return self.force_production or self.is_exporting
