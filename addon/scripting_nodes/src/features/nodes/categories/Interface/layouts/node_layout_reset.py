from ......lib.utils.code.format import indent
from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_LayoutReset(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_LayoutReset"
    bl_label = "Reset Layout"

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        self.add_output("ScriptingInterfaceSocket", "Continue")
        self.add_output("ScriptingInterfaceSocket", "Layout")

    def generate(self):
        self.outputs[1].layout = "self.layout"
        self.code = f"""
            {indent(self.outputs[0].eval(), 3)}
            {indent(self.outputs[1].eval(), 3)}
        """
