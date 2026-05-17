"""Tree dependency queries derived from the reference system.

Used by the smart-reload mechanism to compute which generated tree modules
need to reload alongside a changed tree. There's no stored dependency map -
queries walk the live graph, using the reference system as the source of truth.
"""
from ....lib.utils.node_tree.scripting_node_trees import (
    node_by_id,
    scripting_node_trees,
    sn_nodes,
)
import bpy


def _cross_tree_targets(node):
    """Yield nodes (in other trees) that `node` references via sn_reference_properties."""
    for prop in getattr(node, "sn_reference_properties", set()):
        ref = bpy.context.scene.sna.references.get(getattr(node, prop, ""))
        if not ref:
            continue
        target = node_by_id(ref.node_id)
        if target and target.id_data is not node.id_data:
            yield target


def get_dependent_trees(tree):
    """Module names of trees with nodes referencing any node in `tree`.

    Over-reports for ref types that don't actually emit a cross-tree import
    (e.g. Property references resolve via bpy.types.Scene globally). That's
    fine - extra reloads are correct, just wasteful.
    """
    dependents = set()
    for other_tree in scripting_node_trees():
        if other_tree is tree:
            continue
        for node in sn_nodes(other_tree):
            if any(t.id_data is tree for t in _cross_tree_targets(node)):
                dependents.add(other_tree.module_name)
                break
    return dependents


def get_reload_set(tree):
    """Module names that need reload when `tree` changes (the tree + its dependents)."""
    return {tree.module_name} | get_dependent_trees(tree)
