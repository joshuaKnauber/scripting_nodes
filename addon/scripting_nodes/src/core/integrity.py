"""Repairs that keep the graph consistent before code is generated.

Run on every full flush (file load, undo, redo, ...):
  - initialize trees created through Blender's own "New" button
  - give duplicated trees / nodes / properties (Duplicate, append, link)
    their own ids and point references of nodes copied together at the copies
  - bring data saved by older versions up to date (versioning)
"""

from ..lib.ids import get_short_id
from ..lib.trees import sn_nodes
from . import references, versioning


def ensure(trees):
    tree_ids = set()
    node_ids = set()
    copies = {}  # {tree: {original id: copy id}}
    for tree in trees:
        if not tree.initialized:
            tree.init()
        if not tree.id or tree.id in tree_ids:
            tree.id = get_short_id()
        tree_ids.add(tree.id)
        for node in sn_nodes(tree):
            # set by node.copy() (Duplicate, paste, ...)
            original = node.pop("sn_copied_from", None)
            if not node.id or node.id in node_ids:
                # copied without copy(), e.g. with its tree
                original = node.id or None
                node.id = get_short_id()
            if original:
                copies.setdefault(tree, {})[original] = node.id
            node_ids.add(node.id)
    for tree, tree_copies in copies.items():
        references.remap_copies(tree, tree_copies)
    _unique_property_ids()
    versioning.upgrade(trees)


def _unique_property_ids():
    """Copied nodes / trees duplicate the ids of their properties."""
    from . import properties

    seen = set()
    for _kind, _owner, items in properties.lists():
        for prop in items:
            if not prop.id or prop.id in seen:
                prop.id = get_short_id()
            seen.add(prop.id)


def has_duplicate_ids(trees) -> bool:
    """Cheap check (tree ids only) used by the depsgraph handler."""
    ids = [tree.id for tree in trees]
    return len(ids) != len(set(ids)) or any(not tree.initialized for tree in trees)
