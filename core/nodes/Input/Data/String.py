import bpy

from .....constants import sockets
from ...base_node import SNA_BaseNode


class SNA_NodeString(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeString"
    bl_label = "String"

    value: bpy.props.StringProperty(
        default="",
        name="Value",
        description="The string value of this socket",
        options={"TEXTEDIT_UPDATE"},
        update=lambda self, context: self.mark_dirty(),
    )

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        layout.prop(self, "value", text="")

    def on_create(self):
        self.add_output(sockets.STRING)

    def generate(self, context, trigger):
        self.outputs[0].code = f'"{self.value}"'  # TODO validate
