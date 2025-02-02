from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_IfElse(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_IfElse"
    bl_label = "If/Else"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingBooleanSocket", "Condition")
        self.add_output("ScriptingProgramSocket", "Then")
        self.add_output("ScriptingProgramSocket", "Else")
        self.add_output("ScriptingProgramSocket", "Finally")

    def generate(self):
        has_else = self.outputs[1].is_linked
        self.code = f"""
            if {self.inputs[1].eval()}:
                {indent(self.outputs[0].eval("pass"), 4)}
            {"else:" if has_else else ""}
                {indent(self.outputs[1].eval("pass"), 4) if has_else else ""}
            {indent(self.outputs[2].eval(), 3)}
        """
