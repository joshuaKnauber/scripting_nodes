import hashlib
from ..nodes.references.reference_properties import (
    SNA_NodeReference,
)
from ..nodes.base_node import ScriptingBaseNode
from ..nodes._reference_signatures import (
    DATA_PANEL_PROPERTY_NODES,
    VARIABLE_NODES,
)
from .ui_settings.ui_properties import SNA_UISettings
from .sn_settings.dev_properties import SNA_DevSettings
from .addon_settings.addon_properties import SNA_AddonSettings
import bpy


def signature_key(bl_idnames):
    """Stable attribute name for a frozenset of allowed bl_idnames.

    The same tuple always hashes to the same key, so unrelated nodes that
    accept the same node-type filter share one collection.
    """
    digest = hashlib.sha1(",".join(sorted(bl_idnames)).encode()).hexdigest()[:10]
    return f"refs_{digest}"


_EXTRA_SIGNATURES = (
    # Data panel Properties UIList (property nodes + property groups).
    DATA_PANEL_PROPERTY_NODES,
    # Data panel Variables UIList. Also covered by Get/Set Variable, but
    # listing here keeps the collection alive even if no consumer exists.
    VARIABLE_NODES,
)


def _collect_signatures():
    """Walk every SN node class and gather each declared reference signature.

    Two sources contribute:
      - sn_reference_properties: {prop_name: tuple-of-allowed-bl_idnames} on
        any consumer node.
      - sn_class_body_signature: tuple-of-allowed-bl_idnames on container
        nodes (Operator / Preferences / PropertyGroup) that hold a list of
        attached property refs.

    A small set of `_EXTRA_SIGNATURES` is added on top for UI lists that
    aren't tied to any consumer node (data panel templates).

    Returns {sig_key: frozenset(bl_idnames)}.
    """
    sigs = {}
    for cls in ScriptingBaseNode.__subclasses__():
        for tup in getattr(cls, "sn_reference_properties", {}).values():
            if not tup:
                continue
            sigs[signature_key(tup)] = frozenset(tup)
        cb_sig = getattr(cls, "sn_class_body_signature", ())
        if cb_sig:
            sigs[signature_key(cb_sig)] = frozenset(cb_sig)
    for tup in _EXTRA_SIGNATURES:
        sigs[signature_key(tup)] = frozenset(tup)
    return sigs


class SNA_Settings(bpy.types.PropertyGroup):

    addon: bpy.props.PointerProperty(type=SNA_AddonSettings)

    dev: bpy.props.PointerProperty(type=SNA_DevSettings)

    ui: bpy.props.PointerProperty(type=SNA_UISettings)


# {sig_key: frozenset(bl_idnames)}. Populated at import time and consulted
# by base-node reference helpers + broadcast loops to route to the right
# per-signature CollectionProperty under scene.sna.
SIGNATURE_INDEX = _collect_signatures()

# Inject one CollectionProperty per signature onto SNA_Settings BEFORE
# auto_load registers it. Native `prop_search` only filters by which
# collection it's pointed at, so each declared signature needs its own
# slot so dropdowns show only the relevant nodes.
for _key in SIGNATURE_INDEX:
    SNA_Settings.__annotations__[_key] = bpy.props.CollectionProperty(
        type=SNA_NodeReference
    )


# Convenience attribute names for the data-panel collections, computed at
# import time so UI code can reach them without recomputing the hash.
DATA_PANEL_PROPERTIES_ATTR = signature_key(DATA_PANEL_PROPERTY_NODES)
DATA_PANEL_VARIABLES_ATTR = signature_key(VARIABLE_NODES)


def iter_reference_collections(settings=None):
    """Yield (sig_key, frozenset, collection) for every signature collection."""
    if settings is None:
        settings = bpy.context.scene.sna
    for key, sig in SIGNATURE_INDEX.items():
        yield key, sig, getattr(settings, key)


def collections_for_bl_idname(bl_idname, settings=None):
    """Yield collections whose signature contains `bl_idname`."""
    if settings is None:
        settings = bpy.context.scene.sna
    for key, sig in SIGNATURE_INDEX.items():
        if bl_idname in sig:
            yield getattr(settings, key)


def register():
    bpy.types.Scene.sna = bpy.props.PointerProperty(type=SNA_Settings)


def unregister():
    del bpy.types.Scene.sna
