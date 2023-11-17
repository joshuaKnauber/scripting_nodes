import bpy

from .....constants import sockets
from ...base_node import SNA_BaseNode


class SNA_NodeRow(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeRow"
    bl_label = "Row"

    def on_create(self):
        self.add_input(sockets.INTERFACE)
        self.add_output(sockets.INTERFACE)

    def generate(self, context):
        layout = self.inputs["Interface"].get_meta("layout", "self.layout")
        self.code = f"""
            row_{self.id} = {layout}.row()
            {self.outputs["Interface"].get_code(3)}
        """

        self.outputs["Interface"].set_meta("layout", f"row_{self.id}")
