import bpy
import re
from uuid import uuid4


def get_short_id():
    """Returns a unique id"""
    return uuid4().hex[:8].upper()


def _sanitize_identifier(raw):
    """Coerce arbitrary input into a Python-identifier-safe token.

    Whitespace and hyphens become underscores; any other non-alphanumeric
    char is dropped; runs of underscores collapse; leading digits are
    stripped (Python identifiers can't start with one)."""
    s = re.sub(r"[\s\-]+", "_", raw)
    s = re.sub(r"[^a-zA-Z0-9_]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s.lstrip("0123456789")


class SNA_AddonSettings(bpy.types.PropertyGroup):

    def update_is_dirty(self, context):
        self.is_dirty = True

    def _refresh_all_codegen(self):
        """Re-run generate() on every SN node. Required when an addon-level
        setting (class prefix, idname namespace, ...) feeds into emitted code
        - nodes cache their generated strings, so without this the rewritten
        files would still embed the old prefix."""
        # Lazy import: this module loads before features/nodes during register.
        from ....lib.utils.node_tree.scripting_node_trees import (
            scripting_node_trees,
            sn_nodes,
        )

        for ntree in scripting_node_trees():
            for node in sn_nodes(ntree):
                node._generate()

    def _normalize_module_name(self, context):
        cleaned = _sanitize_identifier(self.module_name_overwrite).lower()
        if cleaned != self.module_name_overwrite:
            self.module_name_overwrite = cleaned
        else:
            self._refresh_all_codegen()
            self.is_dirty = True

    def _normalize_class_prefix(self, context):
        cleaned = _sanitize_identifier(self.class_prefix_overwrite).upper()
        if cleaned != self.class_prefix_overwrite:
            self.class_prefix_overwrite = cleaned
        else:
            self._refresh_all_codegen()
            self.is_dirty = True

    def _normalize_idname_namespace(self, context):
        cleaned = _sanitize_identifier(self.idname_namespace_overwrite).lower()
        if cleaned != self.idname_namespace_overwrite:
            self.idname_namespace_overwrite = cleaned
        else:
            self._refresh_all_codegen()
            self.is_dirty = True

    ### General Settings

    addon_name: bpy.props.StringProperty(
        name="Addon Name",
        description="The name of the addon",
        default="My Addon",
        update=update_is_dirty,
    )

    ### Build Settings

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
        update=_normalize_module_name,
    )

    class_prefix_overwrite: bpy.props.StringProperty(
        name="Class Prefix",
        description=(
            "Prefix used for generated Blender class names (e.g. 'MYADDON' produces "
            "MYADDON_PT_Panel_xxx). Defaults to the uppercased module name"
        ),
        default="",
        update=_normalize_class_prefix,
    )

    idname_namespace_overwrite: bpy.props.StringProperty(
        name="Idname Namespace",
        description=(
            "Namespace used for generated Blender idnames (e.g. 'myaddon' produces "
            "myaddon.operator_xxx). Defaults to the module name"
        ),
        default="",
        update=_normalize_idname_namespace,
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
    def class_prefix(self):
        return self.class_prefix_overwrite or self.module_name.upper()

    @property
    def idname_namespace(self):
        return self.idname_namespace_overwrite or self.module_name
