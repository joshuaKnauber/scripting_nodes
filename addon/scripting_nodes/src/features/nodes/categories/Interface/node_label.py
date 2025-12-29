from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Label(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Label"
    bl_label = "Label"

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        self.add_input("ScriptingStringSocket", "Label")
        self.add_output("ScriptingInterfaceSocket")

    def generate(self):
        self.code = f"""
            {self.inputs[0].get_layout()}.label(text={self.inputs["Label"].eval()})
            {indent(self.outputs[0].eval(), 3)}
        """
