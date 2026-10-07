"""Node-to-node references.

A reference field (e.g. Get Variable's `var`) stores the *id* of the target
node in a hidden `<prop>_ref_id` string. The visible `<prop>` string is a
get/set wrapper: reading it returns the target's current display name
("Name (Tree)"), writing a display name stores the matching id. Renaming the
target node or tree therefore never breaks a reference.

The per-signature collections on scene.sna only exist to feed `prop_search`
pickers; they're rebuilt from the graph by `sync()` on every flush.
"""

import bpy

from ..lib.trees import scripting_node_trees, sn_nodes

REF_ID_SUFFIX = "_ref_id"


def display_name(node) -> str:
    return f"{node.name} ({node.id_data.name})"


def find_node(node_id: str):
    if not node_id:
        return None
    for tree in scripting_node_trees():
        for node in sn_nodes(tree):
            if node.id == node_id:
                return node
    return None


def find_node_by_display_name(name: str):
    if not name:
        return None
    for tree in scripting_node_trees():
        if not name.endswith(f" ({tree.name})"):
            continue
        node = tree.nodes.get(name[: -len(tree.name) - 3])
        if node is not None and getattr(node, "is_sn", False):
            return node
    return None


def ref_id_key(prop: str) -> str:
    return prop + REF_ID_SUFFIX


def make_reference_property(prop: str, original=None):
    """A StringProperty showing the target's display name, storing its id.

    `original` is the deferred property the node declared; its name,
    description and update callback are kept.
    """
    key = ref_id_key(prop)

    def get(self):
        target = find_node(self.get(key, ""))
        return display_name(target) if target else ""

    def set(self, value):
        target = find_node_by_display_name(value)
        self[key] = target.id if target else ""

    kwargs = {}
    if original is not None:
        for name in ("name", "description", "update", "options"):
            if name in original.keywords:
                kwargs[name] = original.keywords[name]
    return bpy.props.StringProperty(get=get, set=set, **kwargs)


def install_reference_properties(cls, props):
    """Turn each declared reference field of `cls` into an id-backed property."""
    annotations = cls.__dict__.get("__annotations__")
    if annotations is None:
        annotations = {}
        cls.__annotations__ = annotations
    for prop in props:
        original = None
        for base in cls.__mro__:
            original = base.__dict__.get("__annotations__", {}).get(prop)
            if original is not None:
                break
        if original is not None and "get" in getattr(original, "keywords", {}):
            continue  # already converted (inherited from an earlier subclass)
        annotations[prop] = make_reference_property(prop, original)
        annotations[ref_id_key(prop)] = bpy.props.StringProperty(options={"HIDDEN"})


# ---------------------------------------------------------------------------
# Graph queries
# ---------------------------------------------------------------------------


def sync(trees=None):
    """Rebuild the scene.sna picker collections from the current graph."""
    scene = getattr(bpy.context, "scene", None)
    if scene is None or not hasattr(scene, "sna"):
        return
    from ..settings.settings import iter_reference_collections

    trees = trees if trees is not None else scripting_node_trees()
    nodes = [node for tree in trees for node in sn_nodes(tree)]
    for _key, signature, coll in iter_reference_collections(scene.sna):
        wanted = [(n.id, display_name(n)) for n in nodes if n.bl_idname in signature]
        current = [(ref.node_id, ref.name) for ref in coll]
        if current == wanted:
            continue
        coll.clear()
        for node_id, name in wanted:
            ref = coll.add()
            ref.node_id = node_id
            ref.name = name
