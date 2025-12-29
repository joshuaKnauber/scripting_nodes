from scripting_nodes.src.lib.utils.sockets.sockets import from_socket
from ..base_socket import ScriptingBaseSocket
import bpy


class LayoutSocket:
    layout: bpy.props.StringProperty(default="")

    def get_layout(self):
        """Return own layout or that of previous connected socket."""
        if self.is_output:
            if self.layout:
                return self.layout
            else:
                if len(self.node.inputs) > 0 and hasattr(self.node.inputs[0], "get_layout"):
                    connected = from_socket(self.node.inputs[0])
                    if connected and hasattr(connected, "get_layout"):
                        return connected.get_layout()
                return "self.layout"
        else:
            connected = from_socket(self)
            if connected and hasattr(connected, "get_layout"):
                return connected.get_layout()
            return "self.layout"


class ScriptingInterfaceSocket(ScriptingBaseSocket, LayoutSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingInterfaceSocket"
    bl_label = "Interface"
    socket_type = "PROGRAM"

    socket_shape = "DIAMOND"

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)

    def _to_code(self):
        pass

    @classmethod
    def draw_color_simple(cls):
        return (0.95, 0.65, 0, 1)
