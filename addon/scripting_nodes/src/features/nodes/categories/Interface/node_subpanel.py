from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_Subpanel(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Subpanel"
    bl_label = "Subpanel"

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        inp = self.add_input("ScriptingBooleanSocket", "Default Closed")
        inp.value = False
        self.add_output("ScriptingInterfaceSocket", "Header")
        self.add_output("ScriptingInterfaceSocket", "Panel")
        self.add_output("ScriptingInterfaceSocket", "After")

    def generate(self):
        self.code_global = f"""
            import bpy

            class SNA_PT_AddonPanel_{self.id}(bpy.types.Panel):
                bl_idname = "SNA_PT_AddonPanel_{self.id}"
        """

        self.outputs["Header"].layout = f"header_{self.id}"
        self.outputs["Panel"].layout = f"panel_{self.id}"

        self.code = f"""
            header_{self.id}, panel_{self.id} = {self.inputs[0].get_layout()}.panel("SNA_PT_AddonPanel_{self.id}", default_closed={self.inputs[1].eval()})
            {indent(self.outputs["Header"].eval(), 3)}
            if panel_{self.id}:
                {indent(self.outputs["Panel"].eval("pass"), 4)}
            {indent(self.outputs["After"].eval(), 3)}
        """
