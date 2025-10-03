from scripting_nodes.src.lib.utils.sockets.sockets import from_socket
from ..base_socket import ScriptingBaseSocket
import bpy


class LayoutSocket:

    def get_layout(self):
        # return own layout or that of previous connected socket
        own_layout = self.get("layout") or ""
        if self.is_output:
            if own_layout:
                return own_layout
            else:
                if len(self.node.inputs) > 0 and hasattr(self.node.inputs[0], "layout"):
                    connected = from_socket(self.node.inputs[0])
                    if connected and hasattr(connected, "layout"):
                        return connected.layout
                return "self.layout"
        else:
            connected = from_socket(self)
            if connected and hasattr(connected, "layout"):
                return connected.layout
            return "self.layout"

    def set_layout(self, value):
        self["layout"] = value

    layout: bpy.props.StringProperty(default="", get=get_layout, set=set_layout)


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