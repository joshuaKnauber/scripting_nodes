import bpy

from ..._reference_signatures import NUMBER_PROPERTY_NODES
from ._property_field import PropertyFieldNode


class SNA_Node_NumberField(PropertyFieldNode, bpy.types.Node):
    """Draw an integer or float property as a number field."""

    bl_idname = "SNA_Node_NumberField"
    bl_label = "Number Field"
    sn_reference_properties = {"prop": NUMBER_PROPERTY_NODES}
    field_options = (("slider", False),)

    slider: bpy.props.BoolProperty(
        name="Slider", description="Display the value as a slider"
    )
