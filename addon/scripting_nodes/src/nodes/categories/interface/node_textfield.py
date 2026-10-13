import bpy

from ....core.references import Reference
from ..._reference_types import STRING_PROPERTY_NODES
from ._property_field import PropertyFieldNode


class SNA_Node_TextField(PropertyFieldNode, bpy.types.Node):
    """Draw a string property as a text field."""

    bl_idname = "SNA_Node_TextField"
    bl_label = "Text Field"
    prop: Reference(STRING_PROPERTY_NODES, name="Property")
