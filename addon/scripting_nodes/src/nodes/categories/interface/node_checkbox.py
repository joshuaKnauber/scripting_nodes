import bpy

from ....core.references import Reference
from ..._reference_types import BOOL_PROPERTY_NODES
from ._property_field import PropertyFieldNode


class SNA_Node_Checkbox(PropertyFieldNode, bpy.types.Node):
    """Draw a boolean property as a checkbox or toggle button."""

    bl_idname = "SNA_Node_Checkbox"
    bl_label = "Checkbox"
    prop: Reference(BOOL_PROPERTY_NODES, name="Property")
    field_options = (("toggle", False), ("invert_checkbox", False))

    toggle: bpy.props.BoolProperty(name="Toggle", description="Draw as a toggle button")
    invert_checkbox: bpy.props.BoolProperty(
        name="Invert", description="Draw the checkbox inverted"
    )
