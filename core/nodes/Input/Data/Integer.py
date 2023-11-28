import bpy

from .....constants import sockets
from ...base_node import SNA_BaseNode


class SNA_NodeInteger(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeInteger"
    bl_label = "Integer"

    value: bpy.props.IntProperty(
        default=0,
        name="Value",
        description="The integer value of this socket",
        update=lambda self, context: self.mark_dirty(),
    )

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        layout.prop(self, "value", text="")

    def on_create(self):
        self.add_output(sockets.INT)

    def generate(self, context, trigger):
        self.outputs[0].code = f"{self.value}"
