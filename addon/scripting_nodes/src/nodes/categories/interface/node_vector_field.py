import bpy

from ..._reference_signatures import FLOAT_VECTOR_PROPERTY_NODES
from ._property_field import PropertyFieldNode


class SNA_Node_VectorField(PropertyFieldNode, bpy.types.Node):
    """Draw a vector property."""

    bl_idname = "SNA_Node_VectorField"
    bl_label = "Vector Field"
    sn_reference_properties = {"prop": FLOAT_VECTOR_PROPERTY_NODES}
    field_options = (("expand", False), ("slider", False))

    expand: bpy.props.BoolProperty(
        name="Expand", description="Draw the components side by side"
    )
    slider: bpy.props.BoolProperty(
        name="Slider", description="Display the values as sliders"
    )
