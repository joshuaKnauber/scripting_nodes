import bpy

from ....constants import sockets
from ..base_node import SNA_BaseNode


class SNA_NodePropertyGroup(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodePropertyGroup"
    bl_label = "Property Group"

    name: bpy.props.StringProperty(
        name="Name",
        default="New Property Group",
        update=lambda self, context: self.mark_dirty(),
    )

    def on_create(self):
        self.add_output(sockets.PROPERTY, "Property Group")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        layout.prop(self, "name", text="")

    def generate(self, context, trigger):
        self.require_register = True

        # self.outputs["Value"].
        # self.code_register = f"bpy.types.Scene.prop_{self.id} = bpy.props.BoolProperty(name='{self.name}')"
        # self.code_unregister = f"del bpy.types.Scene.prop_{self.id}"
