"""Node-to-node references.

A field that points at another node is declared as an annotation:

    class SNA_Node_GetVariable(ScriptingBaseNode, bpy.types.Node):
        var: Reference(VARIABLE_NODES, name="Variable")

`install()` turns it into two properties:
  - `var_id` (hidden) stores the target's node id, so renaming the target or
    its tree never breaks the reference
  - `var` shows the target's label; writing a label picks that node. Its
    `search` callback lists the candidates in Blender's search field.

The same works on PropertyGroups inside nodes (attached class properties).
A deleted target leaves its id in place: undo brings the reference back, the
field draws as missing until then.
"""

import bpy

from ..lib.trees import node_by_id, scripting_node_trees, sn_nodes

ID_SUFFIX = "_id"


class Reference:
    """Declaration of a reference field.

    types: allowed bl_idnames of the target.
    filter: optional `filter(owner_node, target) -> bool` to narrow the
        candidates further (e.g. only bool properties, only local variables
        of the same tree). `owner_node` is the node holding the field, also
        for fields on a PropertyGroup inside that node.
    """

    def __init__(self, types, *, name="", description="", filter=None):
        self.types = frozenset(types)
        self.name = name
        self.description = description
        self.filter = filter

    def allows(self, owner_node, target) -> bool:
        if target is None or target.bl_idname not in self.types:
            return False
        return self.filter is None or bool(self.filter(owner_node, target))

    def candidates(self, owner):
        """Nodes this field may point at, in tree order."""
        owner_node = node_of(owner)
        return [
            node
            for tree in scripting_node_trees()
            for node in sn_nodes(tree)
            if self.allows(owner_node, node)
        ]

    def choices(self, owner):
        """(label, node) of every candidate."""
        return [
            (self.label(owner.id_data, node), node) for node in self.candidates(owner)
        ]

    def label(self, owner_tree, target) -> str:
        """Text shown for `target`: its label, with the tree when it lives in
        another tree, with the node name when another node of the allowed
        types in its tree has the same label."""
        text = target_label(target)
        tree = target.id_data
        for node in tree.nodes:
            if (
                node != target
                and node.bl_idname in self.types
                and target_label(node) == text
            ):
                text = f"{text} [{target.name}]"
                break
        if tree != owner_tree:
            text = f"{text} ({tree.name})"
        return text

    def properties(self, attr):
        """(visible property, hidden id property) for field `attr`."""
        key = attr + ID_SUFFIX
        field = self

        def get(owner):
            target = node_by_id(owner.get(key, ""))
            if target is None:
                return ""
            return field.label(owner.id_data, target)

        def set(owner, value):
            if not value:
                owner[key] = ""
                return
            for text, node in field.choices(owner):
                if text == value:
                    owner[key] = node.id
                    return
            # text that isn't a candidate keeps the current target

        def search(owner, context, edit_text):
            return [(text, node.bl_label) for text, node in field.choices(owner)]

        visible = bpy.props.StringProperty(
            name=self.name,
            description=self.description,
            get=get,
            set=set,
            search=search,
            update=_changed,
        )
        return visible, bpy.props.StringProperty(options={"HIDDEN"})


def target_label(node) -> str:
    """Name of a node as a reference target (see `reference_label`)."""
    label = getattr(node, "reference_label", None)
    return label() if label else node.label or node.name


def _changed(owner, context):
    node = node_of(owner)
    if node is not None:
        node.mark_dirty()


def node_of(owner):
    """The node holding `owner` (the node itself or a PropertyGroup in one of
    its `sn_reference_collections`)."""
    if isinstance(owner, bpy.types.Node):
        return owner
    # Blender can't build data paths for PropertyGroups inside custom nodes
    pointer = owner.as_pointer()
    for node in getattr(owner.id_data, "nodes", ()):
        for collection in getattr(node, "sn_reference_collections", ()):
            for item in getattr(node, collection):
                if item.as_pointer() == pointer:
                    return node
    return None


# ---------------------------------------------------------------------------
# Declaration
# ---------------------------------------------------------------------------


def install(cls):
    """Replace `Reference` annotations of `cls` and its mixins by properties
    and set `cls.sn_references` = {attr: Reference}."""
    fields = {}
    for base in reversed(cls.__mro__):
        annotations = base.__dict__.get("__annotations__")
        if not annotations or base.__module__.startswith("bpy"):
            continue
        own = base.__dict__.get("_sn_reference_fields")
        if own is None:
            own = {}
            for attr, value in list(annotations.items()):
                if isinstance(value, Reference):
                    visible, hidden = value.properties(attr)
                    annotations[attr] = visible
                    annotations[attr + ID_SUFFIX] = hidden
                    own[attr] = value
            base._sn_reference_fields = own
        fields.update(own)
    cls.sn_references = fields


def fields(owner) -> dict:
    return getattr(type(owner), "sn_references", {})


# ---------------------------------------------------------------------------
# Reading and writing
# ---------------------------------------------------------------------------


def target_id(owner, attr) -> str:
    return owner.get(attr + ID_SUFFIX, "")


def resolve(owner, attr):
    """The node field `attr` of `owner` points to, or None."""
    return node_by_id(target_id(owner, attr))


def is_missing(owner, attr) -> bool:
    """True if the field points at a node that doesn't exist (anymore)."""
    return bool(target_id(owner, attr)) and resolve(owner, attr) is None


def point(owner, attr, target):
    """Point field `attr` of `owner` at `target` (None clears it).
    Raises ValueError if `target` isn't a valid choice."""
    field = fields(owner)[attr]
    if target is not None and not field.allows(node_of(owner), target):
        raise ValueError(
            f"{target.bl_idname} '{target.name}' can't be used for {attr!r}"
        )
    owner[attr + ID_SUFFIX] = target.id if target is not None else ""
    _changed(owner, None)


def owners(node):
    """(owner, attr) of every reference field of `node`: its own fields and
    those of PropertyGroups in its `sn_reference_collections`."""
    result = [(node, attr) for attr in fields(node)]
    for collection in getattr(node, "sn_reference_collections", ()):
        for item in getattr(node, collection):
            result += [(item, attr) for attr in fields(item)]
    return result


# ---------------------------------------------------------------------------
# Usages
# ---------------------------------------------------------------------------

# {target node/tree id: [(user node id, attr)]}, rebuilt lazily after every
# rebuild of the addon (see `invalidate`)
_users = None


def invalidate():
    global _users
    _users = None


def _collect_users():
    users = {}
    for tree in scripting_node_trees():
        for node in sn_nodes(tree):
            for owner, attr in owners(node):
                target = target_id(owner, attr)
                if target:
                    users.setdefault(target, []).append((node.id, attr))
    return users


def users(target):
    """Nodes referencing node `target`: [(user node, attr)]."""
    global _users
    if _users is None:
        _users = _collect_users()
    result = []
    for node_id, attr in _users.get(target.id, ()):
        node = node_by_id(node_id)
        if node is not None:
            result.append((node, attr))
    return result


# ---------------------------------------------------------------------------
# Copies
# ---------------------------------------------------------------------------


def remap_copies(tree, copies):
    """Point references of copied nodes at copies made in the same step.

    `copies` maps original node id -> copy id for nodes copied into `tree`
    (pasted, duplicated with their tree, ...). A copied node referencing a
    node outside `tree` that was copied along now references the copy;
    references within the tree (e.g. Ctrl+D next to the original) stay.
    """
    copied = set(copies.values())
    for node in sn_nodes(tree):
        if node.id not in copied:
            continue
        for owner, attr in owners(node):
            old = target_id(owner, attr)
            new = copies.get(old)
            if new is None:
                continue
            original = node_by_id(old)
            if original is None or original.id_data != tree:
                owner[attr + ID_SUFFIX] = new
