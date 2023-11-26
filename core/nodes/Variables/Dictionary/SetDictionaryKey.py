import bpy
from ..templates.VariableReferenceTemplate import VariableReferenceTemplate

from ...base_node import SNA_BaseNode
from .....constants import sockets


class SNA_SetDictionaryKey(SNA_BaseNode, VariableReferenceTemplate, bpy.types.Node):
    bl_idname = "SNA_SetDictionaryKey"
    bl_label = "Set Dictionary Key"

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        self.add_input(sockets.STRING, "Key")
        self.add_input(sockets.DATA, "Value")
        self.add_output(sockets.PROGRAM)
        self.add_output(sockets.DICT)

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        self.draw_variable_selection(context, layout)

    def generate(self, context, trigger):
        if self.variable.node:
            self.code = f"""
                {self.variable.node.var_name()}[{self.inputs["Key"].get_code()}] = {self.inputs["Value"].get_code()}
                {self.outputs["Program"].get_code(3)}
            """
            self.outputs["Dictionary"].code = self.variable.node.var_name()
        else:
            self.code = f"""
                {self.outputs["Program"].get_code(3)}
            """
