import bpy

from ..._reference_signatures import ENUM_PROPERTY_NODES
from ._property_field import PropertyFieldNode


class SNA_Node_EnumMenu(PropertyFieldNode, bpy.types.Node):
    """Draw an enum property as a dropdown or as a row of buttons."""

    bl_idname = "SNA_Node_EnumMenu"
    bl_label = "Enum Menu"
    sn_reference_properties = {"prop": ENUM_PROPERTY_NODES}
    field_options = (("expand", False), ("icon_only", False))

    expand: bpy.props.BoolProperty(
        name="Expand", description="Show every item as its own button"
    )
    icon_only: bpy.props.BoolProperty(
        name="Icon Only", description="Only draw the icons of the items"
    )
