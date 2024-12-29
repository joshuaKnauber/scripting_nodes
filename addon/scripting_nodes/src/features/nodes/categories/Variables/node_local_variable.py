from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_LocalVariable(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_LocalVariable"
    bl_label = "Local Variable"

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingStringSocket", "Initial Value")
        self.add_output("ScriptingProgramSocket")
        self.add_output("ScriptingStringSocket", "Value")

    def generate(self):
        self.code = f"""
            var_{self.id} = {self.inputs[1].eval()}
            {indent(self.outputs[0].eval(), 3)}
        """
        self.outputs[1].code = f"var_{self.id}"
