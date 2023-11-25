import bpy

from .GlobalVariable import SNA_NodeGlobalVariable
from .LocalVariable import SNA_NodeLocalVariable
from ..utils.references import NodePointer, node_search
from ..base_node import SNA_BaseNode
from ....constants import sockets


class SNA_NodeGetVariable(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeGetVariable"
    bl_label = "Get Variable"

    variable: bpy.props.PointerProperty(
        type=NodePointer, name="Variable", description="Variable to reference"
    )

    scope: bpy.props.EnumProperty(
        items=[
            ("LOCAL", "Local", "Local variable", "HOME", 0),
            ("GLOBAL", "Global", "Global variable", "WORLD", 1),
        ],
        name="Scope",
        description="Scope of the variable",
    )

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        self.add_output(sockets.PROGRAM)
        self.add_output(sockets.DATA, "Value")

    def on_reference_update(self, node: SNA_NodeLocalVariable):
        self.convert_socket(
            self.outputs["Value"], sockets.VARIABLE_SOCKETS[node.variable_type]
        )
        self.mark_dirty()

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row(align=True)
        row.prop(self, "scope", text="", icon_only=True)
        idname = (
            SNA_NodeLocalVariable.bl_idname
            if self.scope == "LOCAL"
            else SNA_NodeGlobalVariable.bl_idname
        )
        node_search(
            row,
            self.variable,
            idname,
        )

    def generate(self, context, trigger):
        self.code = f"""
            {self.outputs["Program"].get_code(3)}
        """

        if self.variable.node:
            self.outputs["Value"].code = self.variable.node.var_name()

        layout = self.inputs["Program"].get_meta("layout", "self.layout")
        self.outputs["Program"].set_meta("layout", layout)
