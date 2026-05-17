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
        class_prefix = bpy.context.scene.sna.addon.class_prefix
        menu_idname = f"{class_prefix}_MT_Menu_{self.id}"

        self.outputs["Menu"].layout = f"menu_{self.id}"

        self.code_global = f"""
            class {menu_idname}(bpy.types.Menu):
                bl_idname = "{menu_idname}"
                bl_label = {self.inputs["Label"].eval()}

                def draw(self, context):
                    menu_{self.id} = self.layout
                    {indent(self.outputs["Menu"].eval("pass"), 5)}
        """

        self.code_inline = f"""
            {self.inputs[0].get_layout()}.menu("{menu_idname}", text={self.inputs["Label"].eval()})
            {indent(self.outputs["After"].eval(), 3)}
        """
