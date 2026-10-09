import bpy

from ._property_field import PropertyFieldNode


class SNA_Node_PointerField(PropertyFieldNode, bpy.types.Node):
    """Draw a pointer property as a search field."""

    bl_idname = "SNA_Node_PointerField"
    bl_label = "Pointer Field"
    sn_property_references = {"prop": "POINTER"}
