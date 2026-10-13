import bpy

from ....core.references import Reference
from ..._reference_types import NUMBER_PROPERTY_NODES
from ._property_field import PropertyFieldNode


class SNA_Node_NumberField(PropertyFieldNode, bpy.types.Node):
    """Draw an integer or float property as a number field."""

    bl_idname = "SNA_Node_NumberField"
    bl_label = "Number Field"
    prop: Reference(NUMBER_PROPERTY_NODES, name="Property")
    field_options = (("slider", False),)

    slider: bpy.props.BoolProperty(
        name="Slider", description="Display the value as a slider"
    )
