import bpy
from ...base_node import SN_BaseNode


class SN_IfElseNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IfElseNode"
    bl_label = "If/Else"

    def on_create(self, context):
        self.add_program_input()
        self.add_boolean_input("Condition")
        self.add_program_output("True")
        self.add_program_output("False")

    def generate(self, context):
        self.inputs[0].code = f"""
            if {self.inputs[1].code}:
                {self.outputs[0].code_block(4)}
            else:
                {self.outputs[1].code_block(4)}
        """
