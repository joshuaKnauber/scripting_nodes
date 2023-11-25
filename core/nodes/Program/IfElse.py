import bpy

from ....constants import sockets
from ..base_node import SNA_BaseNode


class SNA_NodeIfElse(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeIfElse"
    bl_label = "If/Else"

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        self.add_input(sockets.BOOLEAN, "Condition")
        self.add_output(sockets.PROGRAM, "True")
        self.add_output(sockets.PROGRAM, "False")
        self.add_output(sockets.PROGRAM, "After")

    def generate(self, context, trigger):
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
