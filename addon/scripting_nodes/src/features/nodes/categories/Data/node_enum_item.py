from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_EnumItem(ScriptingBaseNode, bpy.types.Node):
    """Create an enum item tuple for use with EnumProperty"""

    bl_idname = "SNA_Node_EnumItem"
    bl_label = "Enum Item"

    def update_props(self, context):
        self._generate()

    name_prop: bpy.props.StringProperty(
        name="Name",
        description="Display name shown in UI and used as identifier",
        default="Option",
        update=update_props,
    )

    description: bpy.props.StringProperty(
        name="Description",
        description="Tooltip text",
        default="",
        update=update_props,
    )

    def on_create(self):
        self.add_output("ScriptingDataSocket", "Item")

    def draw(self, context, layout):
        layout.prop(self, "name_prop", text="Name")
        layout.prop(self, "description", text="Desc")

    def generate(self):
        # Build the enum item tuple
        # Format: (identifier, name, description) - identifier is derived from name
        import re

        identifier = re.sub(r"[^a-zA-Z0-9_]", "_", self.name_prop.upper())
        identifier = re.sub(r"_+", "_", identifier).strip("_")
        if not identifier:
            identifier = "OPTION"
        self.outputs["Item"].code = (
            f'("{identifier}", "{self.name_prop}", "{self.description}")'
        )
