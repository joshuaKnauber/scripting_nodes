from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Column(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Column"
    bl_label = "Column"

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        inp = self.add_input("ScriptingBooleanSocket", "Align")
        inp.value = False
        self.add_input("ScriptingStringSocket", "Heading")
        self.add_output("ScriptingInterfaceSocket", "Column")
        self.add_output("ScriptingInterfaceSocket", "After")

    def generate(self):
        self.outputs[0].layout = f"col_{self.id}"
        self.code = f"""
            col_{self.id} = {self.inputs[0].get_layout()}.column(align={self.inputs["Align"].eval()}, heading={self.inputs["Heading"].eval()})
            {indent(self.outputs[0].eval(), 3)}
            {indent(self.outputs[1].eval(), 3)}
        """
