import bpy

from .....constants import sockets
from ...base_node import SN_BaseNode


class SN_IfElseNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IfElseNode"
    bl_label = "If/Else"

    def on_create(self):
        self.add_input(sockets.INTERFACE)
        self.add_input(sockets.BOOLEAN, "Condition")
        self.add_output(sockets.INTERFACE, "True")
        self.add_output(sockets.INTERFACE, "False")
        self.add_output(sockets.INTERFACE, "After")

    def generate(self, context):
        layout = self.inputs["Interface"].get_meta("layout", "self.layout")

        self.code = f"""
            if {self.inputs["Condition"].get_code()}:
                {self.outputs["True"].get_code(4, "pass")}
            else:
                {self.outputs["False"].get_code(4, "pass")}
            {self.outputs["After"].get_code(3)}
        """

        self.outputs["True"].set_meta("layout", layout)
        self.outputs["False"].set_meta("layout", layout)
        self.outputs["After"].set_meta("layout", layout)
