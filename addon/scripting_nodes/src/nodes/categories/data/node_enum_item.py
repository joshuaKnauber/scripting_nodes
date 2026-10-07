import re

import bpy

from ....sockets.spec import Data
from ...base_node import ScriptingBaseNode


class SNA_Node_EnumItem(ScriptingBaseNode, bpy.types.Node):
    """Create an enum item tuple for use with EnumProperty"""

    bl_idname = "SNA_Node_EnumItem"
    bl_label = "Enum Item"
    sn_outputs = [Data("item", "Item")]

    name_prop: bpy.props.StringProperty(
        name="Name",
        description="Display name shown in UI and used as identifier",
        default="Option",
    )
    description: bpy.props.StringProperty(
        name="Description",
        description="Tooltip text",
        default="",
    )

    def draw(self, context, layout):
        layout.prop(self, "name_prop", text="Name")
        layout.prop(self, "description", text="Desc")

    def identifier(self):
        identifier = re.sub(r"[^a-zA-Z0-9_]", "_", self.name_prop.upper())
        return re.sub(r"_+", "_", identifier).strip("_") or "OPTION"

    def emit(self, ctx):
        # (identifier, name, description), the identifier is derived from the name
        item = (self.identifier(), self.name_prop, self.description)
        ctx.output("item", repr(item))
