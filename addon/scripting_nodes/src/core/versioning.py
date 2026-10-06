"""Upgrade node trees saved by older versions of Scripting Nodes.

Every tree stores the data version it was last saved with
(`ScriptingNodeTree.data_version`). On load, each step from that version up to
`DATA_VERSION` runs in order. Add a new step whenever saved data changes shape
(renamed properties, bl_idnames, socket identifiers, enum items, ...).
"""

from ..lib.logger import log
from ..lib.trees import sn_nodes
from .references import find_node_by_display_name, ref_id_key

DATA_VERSION = 1


def _v1_references_by_id(tree):
    """References used to store the target's display name; now they store ids."""
    for node in sn_nodes(tree):
        for prop in getattr(node, "sn_reference_properties", {}):
            _migrate_reference(node, prop)
        for entry in getattr(node, "class_body_properties", ()):
            _migrate_reference(entry, "prop")


def _migrate_reference(owner, prop):
    old_name = owner.get(prop)
    if not isinstance(old_name, str):
        return
    if not owner.get(ref_id_key(prop)):
        target = find_node_by_display_name(old_name)
        if target is not None:
            owner[ref_id_key(prop)] = target.id
    del owner[prop]


STEPS = {
    1: _v1_references_by_id,
}


def upgrade(trees):
    for tree in trees:
        version = tree.data_version
        if version >= DATA_VERSION:
            continue
        for step in range(version + 1, DATA_VERSION + 1):
            try:
                STEPS[step](tree)
            except Exception as exc:
                log("ERROR", f"Upgrading '{tree.name}' to data version {step}: {exc}")
        tree.data_version = DATA_VERSION
