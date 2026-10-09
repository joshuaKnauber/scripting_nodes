import re
import sys

import bpy

from ..core import scheduler
from ..lib.ids import get_short_id
from .properties import SNA_Property

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


class SNA_AddonSettings(bpy.types.PropertyGroup):
    ### General Settings

    addon_name: bpy.props.StringProperty(
        name="Addon Name",
        description="The name of the addon",
        default="My Addon",
        update=_rebuild,
    )

    ### Build Settings

    enabled: bpy.props.BoolProperty(
        name="Enabled",
        description="Enable or disable the addon",
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
