import bpy

from .....constants import sockets
from ...base_node import SN_BaseNode


class SN_RowNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RowNode"
    bl_label = "Row"

    def on_create(self):
        self.add_input(sockets.INTERFACE)
        self.add_output(sockets.INTERFACE)

    def generate(self, context):
        layout = self.inputs["Interface"].get_meta("layout", "self.layout")
        self.code = f"""
            row_{self.id} = {layout}.row()
            {self.outputs["Interface"].code(3)}
        """

        self.outputs["Interface"].set_meta("layout", f"row_{self.id}")
