"""Property Group: a `bpy.types.PropertyGroup` class holding the properties
attached to it (register_on = Property Group). Pointer and Collection
Property nodes use it as their type through `class_name`.
"""

import bpy

from ....core import naming
from ..._class_body import ClassBodyContainerMixin
from ..._reference_signatures import PROPERTY_NODES
from ...base_node import ScriptingBaseNode

# Property groups come after property nodes (their update callbacks and enum
# items are used in the annotations) and before operators, panels, ... (50).
# A group holding a pointer/collection of another group comes after it.
_BASE_ORDER = 30
_MAX_DEPTH = 15


class SNA_Node_PropertyGroup(
    ClassBodyContainerMixin, ScriptingBaseNode, bpy.types.Node
):
    """A group of properties, used as the type of Pointer and Collection
    Properties."""

    bl_idname = "SNA_Node_PropertyGroup"
    bl_label = "Property Group"
    sn_root = True
    sn_class_body_signature = PROPERTY_NODES
    sn_class_body_target = "PropertyGroup"

    prop_label: bpy.props.StringProperty(
        name="Label",
        description="Name of the group (part of its class name)",
        default="My Group",
    )

    @property
    def class_name(self):
        return self.sn_name("class")

    def sn_names(self):
        return [naming.Class("class", "PG", self.prop_label)]

    @property
    def sn_order(self):
        return _BASE_ORDER + self.group_depth()

    def referenced_groups(self):
        """Property Group nodes this group's properties use as type."""
        groups = []
        for prop in self.attached_properties():
            group = getattr(prop, "group_node", lambda: None)()
            if group is not None:
                groups.append(group)
        return groups

    def group_depth(self, _seen=None):
        """How many levels of groups this group contains (0: none)."""
        seen = _seen or set()
        if self.id in seen or len(seen) > _MAX_DEPTH:
            return 0
        seen = seen | {self.id}
        depths = [g.group_depth(seen) + 1 for g in self.referenced_groups()]
        return min(max(depths, default=0), _MAX_DEPTH)

    def draw(self, context, layout):
        layout.prop(self, "prop_label", text="Label")
        self.draw_class_body_properties(layout, label="Properties")

    def emit(self, ctx):
        ctx.module(f"""
            class {self.class_name}(bpy.types.PropertyGroup):
                {ctx.join(self.annotations(ctx))}
        """)
