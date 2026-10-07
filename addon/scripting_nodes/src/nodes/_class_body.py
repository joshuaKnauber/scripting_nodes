"""Nodes whose class has properties attached (Operator, Preferences,
PropertyGroup).

A container keeps a list of references to property nodes. Property nodes
whose `register_on` matches the container (e.g. "Operator") end up as
annotations in the container's class:

    class MY_OT_Operator_1A2B(bpy.types.Operator):
        my_value_3c4d: bpy.props.IntProperty(name="My Value")

Why the list lives on the container (instead of property nodes pointing at
it): matches Blender's mental model (properties belong to a class), keeps an
operator's inputs visible on one node, and one property can be reused by
several operators.
"""

from typing import Tuple

import bpy

from ..core.references import find_node, make_reference_property
from ..lib.trees import node_by_id


def _entry_changed(self, context):
    """Rebuild when the user picks another property for an entry."""
    tree = self.id_data
    pointer = self.as_pointer()
    for node in getattr(tree, "nodes", ()):
        for entry in getattr(node, "class_body_properties", ()):
            if entry.as_pointer() == pointer:
                node.mark_dirty()
                return


class SNA_ClassBodyPropertyEntry(bpy.types.PropertyGroup):
    """One attached property. `prop` shows the property node's display name
    but stores its id in `prop_ref_id` (see core/references.py)."""

    prop: make_reference_property(
        "prop",
        bpy.props.StringProperty(
            name="Property",
            description="Property node attached to this class",
            update=_entry_changed,
        ),
    )
    prop_ref_id: bpy.props.StringProperty(options={"HIDDEN"})


class SNA_OT_AddClassBodyProperty(bpy.types.Operator):
    """Attach another property"""

    bl_idname = "sna.add_class_body_property"
    bl_label = "Add Property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None or not hasattr(node, "class_body_properties"):
            return {"CANCELLED"}
        node.class_body_properties.add()
        node.mark_dirty()
        return {"FINISHED"}


class SNA_OT_RemoveClassBodyProperty(bpy.types.Operator):
    """Detach this property"""

    bl_idname = "sna.remove_class_body_property"
    bl_label = "Remove Property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if node is None or not hasattr(node, "class_body_properties"):
            return {"CANCELLED"}
        if 0 <= self.index < len(node.class_body_properties):
            node.class_body_properties.remove(self.index)
            node.mark_dirty()
        return {"FINISHED"}


class ClassBodyContainerMixin:
    """Adds the attached-properties list to a node.

    Set `sn_class_body_target` to the `register_on` value properties need
    ("Operator", "Preferences" or "PropertyGroup"). In emit(), put
    `ctx.join(self.annotations(ctx))` into the class body."""

    # allowed property node types for the picker
    sn_class_body_signature: Tuple[str, ...] = ()
    sn_class_body_target = ""

    class_body_properties: bpy.props.CollectionProperty(type=SNA_ClassBodyPropertyEntry)

    @classmethod
    def _class_body_collection_attr(cls):
        from ..settings.settings import signature_key

        return signature_key(cls.sn_class_body_signature)

    def attached_properties(self):
        """Property nodes attached to this class (matching register_on)."""
        nodes = []
        for entry in self.class_body_properties:
            node = find_node(entry.prop_ref_id)
            if (
                node is not None
                and getattr(node, "register_on", "") == self.sn_class_body_target
            ):
                nodes.append(node)
        return nodes

    def annotations(self, ctx):
        """`name: bpy.props.X(...)` lines of the attached properties."""
        return [node.annotation(ctx) for node in self.attached_properties()]

    def draw_class_body_properties(self, layout, label="Properties"):
        header = layout.row(align=True)
        header.label(text=label)
        header.operator(
            "sna.add_class_body_property", text="", icon="ADD"
        ).node_id = self.id
        if not len(self.class_body_properties):
            return
        coll_attr = self._class_body_collection_attr()
        col = layout.column(align=True)
        for i, entry in enumerate(self.class_body_properties):
            row = col.row(align=True)
            row.prop_search(
                entry, "prop", bpy.context.scene.sna, coll_attr, text="", icon="DOT"
            )
            target = find_node(entry.prop_ref_id)
            if (
                target is not None
                and getattr(target, "register_on", "") != self.sn_class_body_target
            ):
                row.alert = True
                row.label(text="", icon="ERROR")
            op = row.operator("sna.remove_class_body_property", text="", icon="X")
            op.node_id = self.id
            op.index = i
