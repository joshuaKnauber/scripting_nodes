import bpy

from ....constants import sockets
from ..base_node import SNA_BaseNode


class SNA_NodeLabel(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeLabel"
    bl_label = "Label"

    def on_create(self):
        self.add_input(sockets.INTERFACE)
        self.add_input(sockets.STRING, "Label")
        self.add_output(sockets.INTERFACE)

    def generate(self, context, trigger):
        layout = self.inputs["Interface"].get_meta("layout", "self.layout")
        self.code = f"""
            {layout}.label(text={self.inputs['Label'].get_code()})
            {self.outputs["Interface"].get_code(3)}
        """

        self.outputs["Interface"].set_meta("layout", layout)
