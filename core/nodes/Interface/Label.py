import bpy
from ..base_node import SN_BaseNode


class SN_LabelNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_LabelNodeNew"
    bl_label = "Label"

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Text")

    def generate(self, context):
        self.inputs[0].code = f"""
            layout.label(text={self.inputs[1].code})
        """
