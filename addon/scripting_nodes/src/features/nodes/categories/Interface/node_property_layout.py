from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_PropertyLayout(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_PropertyLayout"
    bl_label = "Set Property Layout"

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        inp = self.add_input("ScriptingBooleanSocket", "Decorated")
        inp.value = False
        inp = self.add_input("ScriptingBooleanSocket", "Split")
        inp.value = False
        self.add_output("ScriptingInterfaceSocket")

    def generate(self):
        self.code = f"""
            {self.inputs[0].layout}.use_property_decorate = {self.inputs["Decorated"].eval()}
            {self.inputs[0].layout}.use_property_split = {self.inputs["Split"].eval()}
            {indent(self.outputs[0].eval(), 3)}
        """
