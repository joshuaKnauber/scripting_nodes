import bpy
from ...base_node import SN_BaseNode


class SN_RepeatNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RepeatNode"
    bl_label = "Loop Repeat"

    def on_create(self, context):
        self.add_program_input()
        self.add_integer_input("Times")
        self.add_program_output("Continue")
        self.add_program_output("Repeat")
        self.add_integer_output("Index")

    def generate(self, context):
        self.inputs[0].code = f"""
            for i_{self.id} in range({self.inputs[1].get_value()}):
                {self.outputs["Repeat"].code_block(4, "pass")}
            {self.outputs["Continue"].code_block(3)}
        """
        self.outputs["Index"].code = f"i_{self.id}"
