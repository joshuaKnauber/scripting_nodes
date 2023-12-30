import bpy

from ..GlobalVariable import SNA_NodeGlobalVariable
from ..LocalVariable import SNA_NodeLocalVariable
from ...utils.references import NodePointer, node_search
from .....constants import sockets


class VariableReferenceTemplate:
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
        update=lambda self, context: self.mark_dirty(),
    )

    def on_variable_update_input(self, node: SNA_NodeLocalVariable):
        self.convert_socket(
            self.inputs["Value"], sockets.SOCKET_IDNAMES[node.variable_type]
        )

    def on_variable_update_output(self, node: SNA_NodeLocalVariable):
        self.convert_socket(
            self.outputs["Value"], sockets.SOCKET_IDNAMES[node.variable_type]
        )

    def draw_variable_selection(
        self, context: bpy.types.Context, layout: bpy.types.UILayout
    ):
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
