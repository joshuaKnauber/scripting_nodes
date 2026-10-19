import datetime
import re
import sys

import bpy

from ..core import metadata, scheduler
from ..lib.ids import get_short_id
from .assets import SNA_Asset
from .folders import SNA_TreeFolder
from .properties import SNA_Property
from .scripts import SNA_Script

# Module names that would shadow something Blender or Python needs
_RESERVED_MODULES = {"bpy", "bmesh", "mathutils", "gpu", "gpu_extras", "blf", "aud"}
_RESERVED_MODULES |= {"bl_math", "freestyle", "idprop", "imbuf", "addon_utils"}


def _safe_module_name(name):
    if (
        name in _RESERVED_MODULES
        or name in sys.stdlib_module_names
        or name.startswith(("bl_", "_"))
    ):
        return name + "_addon"
    return name


def _sanitize_identifier(raw):
    """Coerce arbitrary input into a Python-identifier-safe token.

    Whitespace and hyphens become underscores; any other non-alphanumeric
    char is dropped; runs of underscores collapse; leading digits are
    stripped (Python identifiers can't start with one)."""
    s = re.sub(r"[\s\-]+", "_", raw)
    s = re.sub(r"[^a-zA-Z0-9_]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s.lstrip("0123456789")


def _rebuild(self, context):
    # Addon-level settings (name, prefix, namespace, ...) feed into the code
    # of many nodes, so regenerate everything.
    scheduler.request_full()


def _normalized(prop, transform):
    def update(self, context):
        cleaned = transform(_sanitize_identifier(getattr(self, prop)))
        if cleaned != getattr(self, prop):
            setattr(self, prop, cleaned)  # re-enters this callback once
        else:
            scheduler.request_full()

    return update


def _copyright_update(self, context):
    # the manifest wants "Year Name": add this year to a name typed alone
    text = self.copyright.strip()
    if text and not text[0].isdigit():
        self.copyright = f"{datetime.date.today().year} {text}"  # runs again
    else:
        scheduler.request_full()


def _permission(name, description):
    return bpy.props.BoolProperty(
        name=name, description=f"The add-on {description.lower()}", update=_rebuild
    )


def _reason():
    return bpy.props.StringProperty(
        name="Reason",
        description="Why the add-on needs it (at most 64 characters)",
        update=_rebuild,
    )


class SNA_AddonSettings(bpy.types.PropertyGroup):
    ### General Settings

    addon_name: bpy.props.StringProperty(
        name="Addon Name",
        description="The name of the addon",
        default="My Addon",
        update=_rebuild,
    )

    ### Metadata (core/metadata.py: blender_manifest.toml and bl_info)

    tagline: bpy.props.StringProperty(
        name="Tagline",
        description="One line about the add-on (at most 64 characters)",
        update=_rebuild,
    )
    author: bpy.props.StringProperty(
        name="Author", description="Your name", update=_rebuild
    )
    email: bpy.props.StringProperty(
        name="Email", description="Shown with your name (optional)", update=_rebuild
    )
    version: bpy.props.IntVectorProperty(
        name="Version",
        description="Version of the add-on (major, minor, patch)",
        size=3,
        min=0,
        default=(1, 0, 0),
        update=_rebuild,
    )
    website: bpy.props.StringProperty(
        name="Website",
        description="Documentation or project page",
        subtype="NONE",
        update=_rebuild,
    )
    location: bpy.props.StringProperty(
        name="Location",
        description="Where to find the add-on in Blender, e.g. 'View3D > Sidebar'",
        update=_rebuild,
    )
    tags: bpy.props.EnumProperty(
        name="Tags",
        description="Categories of the add-on (the first is its category)",
        items=[(tag, tag, "") for tag in metadata.TAGS],
        options={"ENUM_FLAG"},
        update=_rebuild,
    )
    copyright: bpy.props.StringProperty(
        name="Copyright",
        description="Who holds the copyright; the current year is added in front",
        update=_copyright_update,
    )
    blender_version_min: bpy.props.IntVectorProperty(
        name="Blender Minimum",
        description=(
            "Oldest Blender version the add-on works in (default: the one "
            "it's made in, the generated code may use what's new in it)"
        ),
        size=3,
        min=0,
        default=(*bpy.app.version[:2], 0),
        update=_rebuild,
    )
    use_blender_version_max: bpy.props.BoolProperty(
        name="Maximum",
        description="Limit the Blender versions the add-on can be installed in",
        update=_rebuild,
    )
    blender_version_max: bpy.props.IntVectorProperty(
        name="Blender Maximum",
        description="First Blender version the add-on doesn't work in",
        size=3,
        min=0,
        default=(6, 0, 0),
        update=_rebuild,
    )
    # what the add-on does that Blender asks the user's permission for, and
    # why (metadata.PERMISSIONS)
    permission_files: _permission("Files", "Reads or writes files")
    files_reason: _reason()
    permission_network: _permission("Network", "Connects to the internet")
    network_reason: _reason()
    permission_clipboard: _permission("Clipboard", "Uses the clipboard")
    clipboard_reason: _reason()
    permission_camera: _permission("Camera", "Records with the camera")
    camera_reason: _reason()
    permission_microphone: _permission("Microphone", "Records with the microphone")
    microphone_reason: _reason()

    ### Build Settings

    enabled: bpy.props.BoolProperty(
        name="Live",
        description="Run the add-on in Blender while you edit it, rebuilt on "
        "every change (exporting works either way)",
        default=True,
        update=_rebuild,
    )

    module_name_overwrite: bpy.props.StringProperty(
        name="Module Name",
        description="An optional name for the folder the addon should be created in",
        default="",
        update=_normalized("module_name_overwrite", str.lower),
    )

    class_prefix_overwrite: bpy.props.StringProperty(
        name="Class Prefix",
        description=(
            "Prefix used for generated Blender class names (e.g. 'MYADDON' produces "
            "MYADDON_PT_Panel_xxx). Defaults to the uppercased module name"
        ),
        default="",
        update=_normalized("class_prefix_overwrite", str.upper),
    )

    idname_namespace_overwrite: bpy.props.StringProperty(
        name="Idname Namespace",
        description=(
            "Namespace used for generated Blender idnames (e.g. 'myaddon' produces "
            "myaddon.operator_xxx). Defaults to the module name"
        ),
        default="",
        update=_normalized("idname_namespace_overwrite", str.lower),
    )

    persist_addon: bpy.props.BoolProperty(
        name="Persist Addon",
        description="Keep the addon enabled when switching files",
        default=False,
        update=_rebuild,
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

    ### Properties (settings/properties.py)

    properties: bpy.props.CollectionProperty(type=SNA_Property)
    active_property: bpy.props.IntProperty()

    ### Folders of the tree list (core/folders.py)

    folders: bpy.props.CollectionProperty(type=SNA_TreeFolder)

    ### Scripts (settings/scripts.py, in the Files list)

    scripts: bpy.props.CollectionProperty(type=SNA_Script)

    ### Assets (settings/assets.py, core/assets.py)

    assets: bpy.props.CollectionProperty(type=SNA_Asset)
    active_asset: bpy.props.IntProperty()

    ### Calculated Values

    @property
    def module_name(self):
        if self.module_name_overwrite:
            name = self.module_name_overwrite
        else:
            words = re.sub(r"[^a-zA-Z\s]", "", self.addon_name).split()
            name = "_".join(words).lower()
        return _safe_module_name(name or "sna_addon")

    @property
    def class_prefix(self):
        return self.class_prefix_overwrite or self.module_name.upper()

    @property
    def idname_namespace(self):
        return self.idname_namespace_overwrite or self.module_name
