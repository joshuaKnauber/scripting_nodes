import bpy
from ..templates.VariableReferenceTemplate import VariableReferenceTemplate

from ...base_node import SNA_BaseNode
from .....constants import sockets


class SNA_DeleteDictionaryKey(SNA_BaseNode, VariableReferenceTemplate, bpy.types.Node):
    bl_idname = "SNA_DeleteDictionaryKey"
    bl_label = "Delete Dictionary Key"

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        self.add_input(sockets.STRING, "Key")
        self.add_output(sockets.PROGRAM)
        self.add_output(sockets.DICT)
        self.add_output(sockets.DATA, "Removed Value")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        self.draw_variable_selection(context, layout)

    def generate(self, context, trigger):
        if self.variable.node:
            self.code = f"""
                value_{self.id} = {self.variable.node.var_name()}.pop({self.inputs["Key"].get_code()}, None)
                {self.outputs["Program"].get_code(3)}
            """
            self.outputs["Dictionary"].code = self.variable.node.var_name()
            self.outputs["Removed Value"].code = f"value_{self.id}"
        else:
            self.code = f"""
                {self.outputs["Program"].get_code(3)}
            """
