"""Shared machinery for nodes that act as class-body containers.

Operator / Preferences / PropertyGroup nodes can have property nodes attached
to them. Each container exposes a list of references to property nodes (each
ref's `register_on` must be the matching class-body type). At generate time
the container resolves each ref and injects the corresponding property
annotation into its emitted class body.

Why a per-container collection (rather than property nodes pointing at the
container): matches Blender's mental model (properties belong to a class),
keeps all of an operator's interface visible on one node, and reuse of a
single property across operators comes for free.
"""
from typing import Tuple
from ...lib.utils.node_tree.scripting_node_trees import (
    node_by_id,
    scripting_node_trees,
    sn_nodes,
)
import bpy


# -----------------------------------------------------------------------------
# Entry PropertyGroup - one per attached property on a container node
# -----------------------------------------------------------------------------


def _entry_prop_changed(self, context):
    """Regenerate the owning container when the user picks a new property.

    The entry doesn't know its owner directly. Walk the node tree it belongs
    to (id_data) and find which node's class_body_properties contains us.
    """
    tree = self.id_data
    if not tree or not hasattr(tree, "nodes"):
        return
    self_ptr = self.as_pointer()
    for node in tree.nodes:
        entries = getattr(node, "class_body_properties", None)
        if entries is None:
            continue
        for entry in entries:
            if entry.as_pointer() == self_ptr:
                if hasattr(node, "_generate"):
                    node._generate()
                return


class SNA_ClassBodyPropertyEntry(bpy.types.PropertyGroup):
    """An entry in a container's class_body_properties collection.

    `prop` stores the ref name (e.g. "My Integer (Main Tree)") - the same
    string that appears in the per-signature reference collection on
    scene.sna chosen by the owning container's sn_class_body_signature.
    """

    prop: bpy.props.StringProperty(
        name="Property",
        description="Property node attached to this container",
        update=_entry_prop_changed,
    )


# -----------------------------------------------------------------------------
# Add / Remove operators
# -----------------------------------------------------------------------------


class SNA_OT_AddClassBodyProperty(bpy.types.Operator):
    """Append an empty entry to a container's property list."""

    bl_idname = "sna.add_class_body_property"
    bl_label = "Add"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if not node or not hasattr(node, "class_body_properties"):
            return {"CANCELLED"}
        node.class_body_properties.add()
        node._generate()
        if node.node_tree:
            node.node_tree.is_dirty = True
        return {"FINISHED"}


class SNA_OT_RemoveClassBodyProperty(bpy.types.Operator):
    """Remove an entry from a container's property list by index."""

    bl_idname = "sna.remove_class_body_property"
    bl_label = "Remove"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if not node or not hasattr(node, "class_body_properties"):
            return {"CANCELLED"}
        if 0 <= self.index < len(node.class_body_properties):
            node.class_body_properties.remove(self.index)
            node._generate()
            if node.node_tree:
                node.node_tree.is_dirty = True
        return {"FINISHED"}


# -----------------------------------------------------------------------------
# Container mixin
# -----------------------------------------------------------------------------


class ClassBodyContainerMixin:
    """Adds a `class_body_properties` collection + helpers to a node.

    Subclasses should call `draw_class_body_properties(layout)` from their
    draw method and `collect_class_body_annotations()` from generate. Each
    container declares `sn_class_body_signature` - the tuple of property
    bl_idnames allowed in its picker - so the per-entry prop_search is
    routed to the matching filtered collection on scene.sna.
    """

    # Tuple of bl_idnames the per-entry picker accepts. Override in each
    # concrete container.
    sn_class_body_signature: Tuple[str, ...] = ()

    class_body_properties: bpy.props.CollectionProperty(
        type=SNA_ClassBodyPropertyEntry
    )

    @classmethod
    def _class_body_collection_attr(cls):
        from ..settings.settings_properties import signature_key
        return signature_key(cls.sn_class_body_signature)

    def draw_class_body_properties(self, layout, label="Properties"):
        """Draw the property list with add/remove buttons + per-row dropdowns."""
        header = layout.row(align=True)
        header.label(text=label)
        add_op = header.operator(
            "sna.add_class_body_property", text="", icon="ADD"
        )
        add_op.node_id = self.id

        if len(self.class_body_properties) == 0:
            return

        coll_attr = self._class_body_collection_attr()
        col = layout.column(align=True)
        for i, entry in enumerate(self.class_body_properties):
            row = col.row(align=True)
            row.prop_search(
                entry,
                "prop",
                bpy.context.scene.sna,
                coll_attr,
                text="",
                icon="DOT",
            )
            rm = row.operator(
                "sna.remove_class_body_property", text="", icon="X"
            )
            rm.node_id = self.id
            rm.index = i

    def iter_attached_property_nodes(self):
        """Yield (entry, property_node) pairs for each resolved entry.

        Entries whose `prop` is empty or resolves to a missing node are skipped
        silently - container generation should treat them as no-ops.
        """
        coll = getattr(bpy.context.scene.sna, self._class_body_collection_attr())
        for entry in self.class_body_properties:
            if not entry.prop:
                continue
            ref = coll.get(entry.prop)
            if not ref:
                continue
            prop_node = ref.node
            if prop_node is None:
                continue
            yield entry, prop_node

    def collect_class_body_annotations(self):
        """Return a list of annotation lines for this container's class body.

        Each line is like `prop_name: bpy.props.IntProperty(...)`. The update
        and poll callback function bodies stay in the property node's
        `code_global` (module scope), already picked up by the tree generator.
        """
        annotations = []
        for entry, prop_node in self.iter_attached_property_nodes():
            if hasattr(prop_node, "class_body_annotation"):
                line = prop_node.class_body_annotation()
                if line:
                    annotations.append(line)
        return annotations
