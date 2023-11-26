import bpy
from ..templates.VariableReferenceTemplate import VariableReferenceTemplate

from ...base_node import SNA_BaseNode
from .....constants import sockets


class SNA_NodeInsertInList(SNA_BaseNode, VariableReferenceTemplate, bpy.types.Node):
    bl_idname = "SNA_NodeInsertInList"
    bl_label = "Insert In List"

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        self.add_input(sockets.INT, "Index")
        self.add_input(sockets.DATA, "Value")
        self.add_output(sockets.PROGRAM)
        self.add_output(sockets.LIST)

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        self.draw_variable_selection(context, layout)

    def generate(self, context, trigger):
        if self.variable.node:
            self.code = f"""
                {self.variable.node.var_name()}.insert({self.inputs["Index"].get_code()}, {self.inputs["Value"].get_code()})
                {self.outputs["Program"].get_code(4)}
            """
            self.outputs["List"].code = self.variable.node.var_name()
        else:
            self.code = f"""
                {self.outputs["Program"].get_code(4)}
            """
