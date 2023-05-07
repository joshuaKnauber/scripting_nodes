import bpy
from ..base_node import SN_BaseNode
from random import uniform


class SN_PrintNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PrintNode"
    bl_label = "Print"

    def on_create(self, context):
        self.add_execute_input()
        self.add_string_input()
        self.add_data_input()
        self.add_execute_output()

    def generate(self, context):
        self.inputs[0].code = f"""
            # {uniform(0, 1)}
            print({self.inputs[1].code})
            {self.outputs[0].code_block(3)}
        """

    def draw_node(self, context, layout):
        for line in self.inputs[0].code.split("\n"):
            layout.label(text=line)
