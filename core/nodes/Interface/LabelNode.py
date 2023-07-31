import bpy

from ....constants import sockets
from ..base_node import SN_BaseNode


class SN_LabelNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_LabelNode"
    bl_label = "Label"

    def update_text(self, context):
        self.generate(context)

    dummy: bpy.props.StringProperty(default="test", update=update_text)

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        layout.prop(self, "dummy")

    def on_create(self):
        self.add_input(sockets.INTERFACE)

    def generate(self, context):
        sn = context.scene.sn
        self.code = f"""
            self.layout.label(text="{self.dummy}")
        """
