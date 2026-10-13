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

import bpy

from ..core.context import NodeError
from ..core.references import Reference, install, resolve
from ..lib.trees import node_by_id
from ._reference_types import PROPERTY_NODES
from .base_node import draw_reference


def _attachable(container, prop_node):
    """Only properties registered on this kind of class."""
    return getattr(prop_node, "register_on", "") == container.sn_class_body_target


class SNA_ClassBodyPropertyEntry(bpy.types.PropertyGroup):
    """One attached property (a reference field, see core/references.py)."""

    prop: Reference(
        PROPERTY_NODES,
        name="Property",
        description="Property node attached to this class",
        filter=_attachable,
    )


install(SNA_ClassBodyPropertyEntry)


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

    sn_class_body_target = ""
    sn_reference_collections = ("class_body_properties",)

    class_body_properties: bpy.props.CollectionProperty(type=SNA_ClassBodyPropertyEntry)

    def attached_properties(self):
        """Property nodes attached to this class (matching register_on)."""
        nodes = []
        for entry in self.class_body_properties:
            node = resolve(entry, "prop")
            if node is not None and _attachable(self, node):
                nodes.append(node)
        return nodes

    def annotations(self, ctx):
        """`name: bpy.props.X(...)` lines of the attached properties.
        Incomplete properties are left out (their node shows why)."""
        lines = []
        for node in self.attached_properties():
            try:
                lines.append(node.annotation(ctx))
            except NodeError:
                continue
        return lines

    def draw_class_body_properties(self, layout, label="Properties"):
        header = layout.row(align=True)
        header.label(text=label)
        header.operator(
            "sna.add_class_body_property", text="", icon="ADD"
        ).node_id = self.id
        if not len(self.class_body_properties):
            return
        col = layout.column(align=True)
        for i, entry in enumerate(self.class_body_properties):
            row = col.row(align=True)
            draw_reference(row, entry, "prop")
            target = resolve(entry, "prop")
            if target is not None and not _attachable(self, target):
                # register_on changed after it was attached
                row.alert = True
                row.label(text="", icon="ERROR")
            op = row.operator("sna.remove_class_body_property", text="", icon="X")
            op.node_id = self.id
            op.index = i
