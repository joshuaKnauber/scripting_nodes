import bpy

from ._property_field import PropertyFieldNode


class SNA_Node_TextField(PropertyFieldNode, bpy.types.Node):
    """Draw a string property as a text field."""

    bl_idname = "SNA_Node_TextField"
    bl_label = "Text Field"
    sn_property_references = {"prop": "STRING"}
