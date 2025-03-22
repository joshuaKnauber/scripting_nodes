from .socket_interface import LayoutSocket
from scripting_nodes.src.lib.utils.sockets.sockets import from_socket, to_socket
from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingProgramSocket(ScriptingBaseSocket, LayoutSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingProgramSocket"
    bl_label = "Program"
    socket_type = "PROGRAM"

    socket_shape = "DIAMOND"

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)

    def _to_code(self):
        pass

    def draw_color(self, context, node):
        connected = None
        if len(node.inputs) > 0:
            from_connected = from_socket(node.inputs[0])
            if from_connected and from_connected.socket_type == "PROGRAM":
                connected = from_connected
        return (
            connected.draw_color(context, connected.node)
            if hasattr(connected, "draw_color")
            else (
                connected.draw_color_simple()
                if hasattr(connected, "draw_color_simple")
                else (0.35, 0.35, 0.35, 1)
            )
        )
