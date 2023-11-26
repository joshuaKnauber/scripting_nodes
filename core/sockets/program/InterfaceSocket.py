import bpy

from ..base_socket import ScriptingSocket
from ...utils.sockets import is_only_with_name


class SNA_InterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_InterfaceSocket"
    is_program = True

    def on_create(self, context: bpy.types.Context):
        self.display_shape = "DIAMOND"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.9, 0.6, 0, 1)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)
        if self.dynamic:
            row = layout.row(align=True)
            op = row.operator(
                "sna.add_dynamic_socket", text="", emboss=False, icon="ADD"
            )  # TODO generalize
            op.node = node.id
            op.is_output = self.is_output
            op.index = self.index
            if not is_only_with_name(self.node, self):
                op = row.operator(
                    "sna.remove_socket", text="", emboss=False, icon="REMOVE"
                )
                op.node = node.id
                op.is_output = self.is_output
                op.index = self.index
