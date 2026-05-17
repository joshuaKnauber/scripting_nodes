from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_Print(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Print"
    bl_label = "Print"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingStringSocket", "Text")
        self.add_output("ScriptingProgramSocket")

    def generate(self):
        text_eval = self.inputs[1].eval()
        next_code = indent(self.outputs[0].eval(), 3)
        self.code_inline = f"""
            print({text_eval})
            {next_code}
        """
