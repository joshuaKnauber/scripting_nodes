import bpy
from ..base_node import SN_BaseNode


class SN_ButtonNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ButtonNodeNew"
    bl_label = "Button"

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input()

        self.add_interface_output()
        self.add_execute_output()

    def generate(self, context):
        self.inputs[0].code = f"""
            layout.operator("sn.dummy_operator", text="{self.inputs[1].code}")
        """
