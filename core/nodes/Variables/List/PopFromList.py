import bpy
from ..templates.VariableReferenceTemplate import VariableReferenceTemplate

from ...base_node import SNA_BaseNode
from .....constants import sockets


class SNA_NodePopFromList(SNA_BaseNode, VariableReferenceTemplate, bpy.types.Node):
    bl_idname = "SNA_NodePopFromList"
    bl_label = "Pop From List"

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        self.add_input(sockets.INT, "Index")
        self.add_output(sockets.PROGRAM)
        self.add_output(sockets.LIST)
        self.add_output(sockets.DATA, "Removed Value")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        self.draw_variable_selection(context, layout)

    def generate(self, context, trigger):
        if self.variable.node:
            self.code = f"""
                value_{self.id} = {self.variable.node.var_name()}.pop({self.inputs["Index"].get_code()})
                {self.outputs["Program"].get_code(4)}
            """
            self.outputs["List"].code = self.variable.node.var_name()
            self.outputs["Removed Value"].code = f"value_{self.id}"
        else:
            self.code = f"""
                {self.outputs["Program"].get_code(4)}
            """
