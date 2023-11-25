import bpy

from .LocalVariable import SNA_NodeLocalVariable
from ..utils.references import NodePointer, node_search
from ..base_node import SNA_BaseNode
from ....constants import sockets, variables


class SNA_NodeGetLocalVariable(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeGetLocalVariable"
    bl_label = "Get Local Variable"

    variable: bpy.props.PointerProperty(
        type=NodePointer, name="Variable", description="Variable to reference"
    )

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        self.add_output(sockets.PROGRAM)
        self.add_output(sockets.FLOAT, "Value")

    def on_reference_update(self, node: SNA_NodeLocalVariable):
        self.convert_socket(
            self.outputs["Value"], variables.VARIABLE_SOCKETS[node.variable_type]
        )
        self.mark_dirty_delayed()

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        node_search(layout, self.variable, SNA_NodeLocalVariable.bl_idname)

    def generate(self, context, trigger):
        self.code = f"""
            {self.outputs["Program"].get_code(3)}
        """

        if self.variable.node:
            self.outputs["Value"].code = self.variable.node.var_name()

        layout = self.inputs["Program"].get_meta("layout", "self.layout")
        self.outputs["Program"].set_meta("layout", layout)
