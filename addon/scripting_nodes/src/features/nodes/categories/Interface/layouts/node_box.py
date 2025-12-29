from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Box(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Box"
    bl_label = "Box"

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        self.add_output("ScriptingInterfaceSocket", "Box")
        self.add_output("ScriptingInterfaceSocket", "After")

    def generate(self):
        self.outputs[0].layout = f"box_{self.id}"
        self.code = f"""
            box_{self.id} = {self.inputs[0].get_layout()}.box()
            {indent(self.outputs[0].eval(), 3)}
            {indent(self.outputs[1].eval(), 3)}
        """
