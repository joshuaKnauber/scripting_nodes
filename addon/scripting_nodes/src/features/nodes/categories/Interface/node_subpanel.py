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
        class_prefix = bpy.context.scene.sna.addon.class_prefix
        panel_idname = f"{class_prefix}_PT_AddonPanel_{self.id}"

        self.code_global = f"""
            class {panel_idname}(bpy.types.Panel):
                bl_idname = "{panel_idname}"
        """

        self.outputs["Header"].layout = f"header_{self.id}"
        self.outputs["Panel"].layout = f"panel_{self.id}"

        self.code_inline = f"""
            header_{self.id}, panel_{self.id} = {self.inputs[0].get_layout()}.panel("{panel_idname}", default_closed={self.inputs[1].eval()})
            {indent(self.outputs["Header"].eval(), 3)}
            if panel_{self.id}:
                {indent(self.outputs["Panel"].eval("pass"), 4)}
            {indent(self.outputs["After"].eval(), 3)}
        """
