import bpy

from ....constants import sockets
from ..base_node import SN_BaseNode


class SN_NodeDrawCheckbox(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_NodeDrawCheckbox"
    bl_label = "Draw Checkbox"

    def on_create(self):
        self.add_input(sockets.INTERFACE)
        self.add_input(sockets.PROPERTY, "Boolean Property")
        label = self.add_input(sockets.STRING, "Label")
        label.show_enable = True
        label.enabled = False
        self.add_output(sockets.INTERFACE)

    def generate(self, context):
        layout = self.inputs["Interface"].get_meta("layout", "self.layout")

        if self.inputs["Boolean Property"].is_linked:
            prop = self.inputs["Boolean Property"]
            text = (
                f", text={self.inputs['Label'].get_code()}"
                if self.inputs["Label"].enabled
                else ""
            )
            self.code = f"""
                {layout}.prop({prop.get_meta('data', 'bpy.context.scene')}, "{prop.get_meta('identifier', 'not_a_property')}"{text})
                {self.outputs["Interface"].get_code(4)}
            """
        else:
            self.code = f"""
                {layout}.label(text="No property connected!")
                {self.outputs["Interface"].get_code(4)}
            """

        self.outputs["Interface"].set_meta("layout", layout)
