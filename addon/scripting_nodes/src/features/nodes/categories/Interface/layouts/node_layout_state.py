from ......lib.utils.code.format import indent
from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_LayoutState(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_LayoutState"
    bl_label = "Set Layout State"

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        inp = self.add_input("ScriptingBooleanSocket", "Enabled")
        inp.value = True
        inp = self.add_input("ScriptingBooleanSocket", "Active")
        inp.value = True
        inp = self.add_input("ScriptingBooleanSocket", "Alert")
        inp.value = False
        self.add_output("ScriptingInterfaceSocket")

    def generate(self):
        self.code = f"""
            {self.inputs[0].get_layout()}.enabled = {self.inputs["Enabled"].eval()}
            {self.inputs[0].get_layout()}.active = {self.inputs["Active"].eval()}
            {self.inputs[0].get_layout()}.alert = {self.inputs["Alert"].eval()}
            {indent(self.outputs[0].eval(), 3)}
        """
