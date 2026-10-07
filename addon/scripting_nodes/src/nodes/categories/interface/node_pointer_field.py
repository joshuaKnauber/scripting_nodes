import bpy

from ..._reference_signatures import POINTER_PROPERTY_NODES
from ._property_field import PropertyFieldNode


class SNA_Node_PointerField(PropertyFieldNode, bpy.types.Node):
    """Draw a pointer property as a search field."""

    bl_idname = "SNA_Node_PointerField"
    bl_label = "Pointer Field"
    sn_reference_properties = {"prop": POINTER_PROPERTY_NODES}
