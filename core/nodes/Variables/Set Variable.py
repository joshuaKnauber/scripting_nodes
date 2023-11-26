import bpy

from .templates.VariableReferenceTemplate import VariableReferenceTemplate

from .LocalVariable import SNA_NodeLocalVariable
from ..base_node import SNA_BaseNode
from ....constants import sockets


class SNA_NodeSetVariable(SNA_BaseNode, VariableReferenceTemplate, bpy.types.Node):
    bl_idname = "SNA_NodeSetVariable"
    bl_label = "Set Variable"

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        self.add_output(sockets.PROGRAM)
        self.add_input(sockets.DATA, "Value")

    def on_reference_update(self, node: SNA_NodeLocalVariable):
        self.on_variable_update_input(node)
        self.mark_dirty()

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        self.draw_variable_selection(context, layout)

    def generate(self, context, trigger):
        if self.variable.node:
            self.code = f"""
                {self.variable.node.var_name()} = {self.inputs["Value"].get_code()}
                {self.outputs["Program"].get_code(3)}
            """
        else:
            self.code = f"""
                {self.outputs["Program"].get_code(3)}
            """

        layout = self.inputs["Program"].get_meta("layout", "self.layout")
        self.outputs["Program"].set_meta("layout", layout)
