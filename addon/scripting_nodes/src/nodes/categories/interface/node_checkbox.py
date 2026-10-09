import bpy

from ._property_field import PropertyFieldNode


class SNA_Node_Checkbox(PropertyFieldNode, bpy.types.Node):
    """Draw a boolean property as a checkbox or toggle button."""

    bl_idname = "SNA_Node_Checkbox"
    bl_label = "Checkbox"
    sn_property_references = {"prop": "BOOLEAN"}
    field_options = (("toggle", False), ("invert_checkbox", False))

    toggle: bpy.props.BoolProperty(name="Toggle", description="Draw as a toggle button")
    invert_checkbox: bpy.props.BoolProperty(
        name="Invert", description="Draw the checkbox inverted"
    )
