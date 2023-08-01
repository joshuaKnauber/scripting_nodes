import bpy

from ....constants import sockets
from ..base_node import SN_BaseNode


class SN_LabelNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_LabelNode"
    bl_label = "Label"

    def on_create(self):
        self.add_input(sockets.INTERFACE)
        self.add_input(sockets.STRING, "Label")
        self.add_output(sockets.INTERFACE)

    def generate(self, context):
        layout = self.inputs["Interface"].get_meta("layout", "self.layout")
        self.code = f"""
            {layout}.label(text={self.inputs['Label'].code()})
            {self.outputs["Interface"].code(3)}
            None.object
        """

        self.outputs["Interface"].set_meta("layout", layout)
