from ....lib.utils.sockets.sockets import from_socket
from ..base_socket import ScriptingBaseSocket
import bpy


class LayoutSocket:
    layout: bpy.props.StringProperty(default="")

    def _get_default_layout(self):
        """Return the default layout reference based on context.

        Inside INTERFACE group trees, we use 'layout' (passed as parameter).
        Outside group trees (or in PROGRAM groups), we use 'self.layout'.
        """
        ntree = self.node.node_tree
        if getattr(ntree, "is_group", False):
            # Find GroupInput node to check group_type
            for node in ntree.nodes:
                if node.bl_idname == "SNA_Node_GroupInput":
                    if getattr(node, "group_type", "") == "INTERFACE":
                        return "layout"
                    break
        return "self.layout"

    def get_layout(self):
        """Return own layout or that of previous connected socket."""
        if self.is_output:
            if self.layout:
                return self.layout
            else:
                if len(self.node.inputs) > 0 and hasattr(
                    self.node.inputs[0], "get_layout"
                ):
                    connected = from_socket(self.node.inputs[0])
                    if connected and hasattr(connected, "get_layout"):
                        return connected.get_layout()
                return self._get_default_layout()
        else:
            connected = from_socket(self)
            if connected and hasattr(connected, "get_layout"):
                return connected.get_layout()
            return self._get_default_layout()


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
