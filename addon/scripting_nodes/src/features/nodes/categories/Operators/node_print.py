from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Print(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Print"
    bl_label = "Print"

    def on_create(self):
        self.add_input("ScriptingLogicSocket")
        self.add_input("ScriptingStringSocket", "Text")
        self.add_output("ScriptingLogicSocket")

    def generate(self):
        self.code = f"""
            print({self.inputs[1].eval()})
            {indent(self.outputs[0].eval(), 3)} 
        """
