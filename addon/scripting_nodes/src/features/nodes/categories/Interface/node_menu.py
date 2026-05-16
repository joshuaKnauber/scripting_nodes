from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_Menu(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Menu"
    bl_label = "Menu"

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        self.add_input("ScriptingStringSocket", "Label").value = "Menu"
        self.add_output("ScriptingInterfaceSocket", "Menu")
        self.add_output("ScriptingInterfaceSocket", "After")

    def generate(self):
        self.outputs["Menu"].layout = f"menu_{self.id}"

        self.code_global = f"""
            import bpy

            class SNA_MT_Menu_{self.id}(bpy.types.Menu):
                bl_idname = "SNA_MT_Menu_{self.id}"
                bl_label = {self.inputs["Label"].eval()}

                def draw(self, context):
                    menu_{self.id} = self.layout
                    {indent(self.outputs["Menu"].eval("pass"), 5)}
        """

        self.code = f"""
            {self.inputs[0].get_layout()}.menu("SNA_MT_Menu_{self.id}", text={self.inputs["Label"].eval()})
            {indent(self.outputs["After"].eval(), 3)}
        """
