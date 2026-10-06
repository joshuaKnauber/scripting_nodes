"""Repairs that keep the graph consistent before code is generated.

Run on every full flush (file load, undo, redo, ...):
  - initialize trees created through Blender's own "New" button
  - give duplicated trees / nodes (Duplicate, append, link) their own ids
  - bring data saved by older versions up to date (versioning)
"""

from ..lib.ids import get_short_id
from ..lib.trees import sn_nodes
from . import versioning


def ensure(trees):
    tree_ids = set()
    node_ids = set()
    for tree in trees:
        if not tree.initialized:
            tree.init()
        if not tree.id or tree.id in tree_ids:
            tree.id = get_short_id()
        tree_ids.add(tree.id)
        for node in sn_nodes(tree):
            if not node.id or node.id in node_ids:
                node.id = get_short_id()
            node_ids.add(node.id)
    versioning.upgrade(trees)


def has_duplicate_ids(trees) -> bool:
    """Cheap check (tree ids only) used by the depsgraph handler."""
    ids = [tree.id for tree in trees]
    return len(ids) != len(set(ids)) or any(not tree.initialized for tree in trees)
