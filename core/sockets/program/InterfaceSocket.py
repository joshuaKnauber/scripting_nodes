import bpy
from bpy.types import Context, UILayout

from ..base_socket import ScriptingSocket


class SNA_InterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_InterfaceSocket"
    bl_label = "Interface"
    is_program = True

    def on_create(self, context: bpy.types.Context):
        self.display_shape = "DIAMOND"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.9, 0.6, 0, 1)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)


# class SNA_GroupInterface_InterfaceSocket(bpy.types.NodeTreeInterfaceSocket):

#     bl_idname = SNA_InterfaceSocket.bl_idname + "Interface"
#     bl_socket_idname = SNA_InterfaceSocket.bl_idname
#     bl_label = SNA_InterfaceSocket.bl_label

#     def draw(self, context: Context, layout: UILayout):
#         layout.label(text="drawing")

#     def color(self, context: Context, node: bpy.types.Node):
#         return (1, 0, 0, 1)
