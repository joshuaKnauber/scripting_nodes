import bpy

from ....constants.properties import id_type_items, id_type_names
from ..base_node import SNA_BaseNode


class SNA_NodeBoolProperty(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeBoolProperty"
    bl_label = "Boolean Property"

    source_type: bpy.props.EnumProperty(
        name="Source",
        description="The type of data this property should be attached to. When selecting e.g. 'Object', each object will have a value for this property. An example for this is the objects location.",
        items=id_type_items,
        default=id_type_names().index("Scene"),
        update=lambda self, _: self.mark_dirty(),
    )

    def on_create(self):
        self.name = "New Boolean"

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row()
        row.prop(self, "name", text="")
        row.operator(
            "sna.node_settings", text="", icon="PREFERENCES", emboss=False
        ).node = self.name
        layout.prop(self, "source_type", text="")

    def identifier(self):
        return f"prop_{self.id}"

    def generate(self, context):
        self.require_register = True

        self.code_register = f"bpy.types.{self.source_type}.{self.identifier()} = bpy.props.BoolProperty(name='{self.name}')"
        self.code_unregister = f"del bpy.types.{self.source_type}.{self.identifier()}"
