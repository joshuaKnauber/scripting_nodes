import bpy

from .templates.VariableReferenceTemplate import VariableReferenceTemplate
from .GlobalVariable import SNA_NodeGlobalVariable
from .LocalVariable import SNA_NodeLocalVariable
from ..base_node import SNA_BaseNode
from ....constants import sockets


class SNA_NodeGetVariable(SNA_BaseNode, VariableReferenceTemplate, bpy.types.Node):
    bl_idname = "SNA_NodeGetVariable"
    bl_label = "Get Variable"

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        self.add_output(sockets.PROGRAM)
        self.add_output(sockets.DATA, "Value")

    def on_reference_update(self, node: SNA_NodeLocalVariable):
        if node:
            self.on_variable_update_output(node)
        self.mark_dirty()

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        self.draw_variable_selection(context, layout)

    def generate(self, context, trigger):
        self.code = f"""
            {self.outputs["Program"].get_code(3)}
        """

        if self.variable.node:
            self.outputs["Value"].code = self.variable.node.var_name()

        layout = self.inputs["Program"].get_meta("layout", "self.layout")
        self.outputs["Program"].set_meta("layout", layout)
