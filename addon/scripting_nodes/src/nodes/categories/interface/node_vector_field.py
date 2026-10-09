import bpy

from ._property_field import PropertyFieldNode


class SNA_Node_VectorField(PropertyFieldNode, bpy.types.Node):
    """Draw a vector property."""

    bl_idname = "SNA_Node_VectorField"
    bl_label = "Vector Field"
    sn_property_references = {"prop": "VECTOR"}
    field_options = (("expand", False), ("slider", False))

    expand: bpy.props.BoolProperty(
        name="Expand", description="Draw the components side by side"
    )
    slider: bpy.props.BoolProperty(
        name="Slider", description="Display the values as sliders"
    )
