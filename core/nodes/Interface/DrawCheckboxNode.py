import bpy

from ....constants import sockets
from ..base_node import SN_BaseNode
from ..Properties.BoolPropertyNode import SN_BoolPropertyNode
from ..utils.references import NodePointer, node_search


class SN_DrawCheckboxNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DrawCheckboxNode"
    bl_label = "Draw Checkbox"

    def on_create(self):
        self.add_input(sockets.INTERFACE)
        self.add_input(sockets.PROPERTY, "Boolean Property")
        self.add_input(sockets.STRING, "Label")
        self.add_output(sockets.INTERFACE)

    def generate(self, context):
        layout = self.inputs["Interface"].get_meta("layout", "self.layout")

        # if self.bool_prop.node:
        #     self.code = f"""
        #         {layout}.prop(bpy.context.scene, "prop_{self.bool_prop.id}", text={self.inputs['Label'].get_code()})
        #         {self.outputs["Interface"].get_code(4)}
        #     """
        # else:
        #     self.code = f"""
        #         {layout}.label(text="No valid property selected!")
        #         {self.outputs["Interface"].get_code(4)}
        #     """

        self.outputs["Interface"].set_meta("layout", layout)
