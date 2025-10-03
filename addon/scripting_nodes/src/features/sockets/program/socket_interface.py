from scripting_nodes.src.lib.utils.sockets.sockets import from_socket
from ..base_socket import ScriptingBaseSocket
import bpy


class LayoutSocket:
    # Blender 5.0: get/set renamed to get_transform/set_transform in bpy.props
    # However, NodeSocket types don't support IDProperties, so using Python @property instead

    @property
    def layout(self):
        # return own layout or that of previous connected socket
        stored = getattr(self, "_layout_value", "")
        if stored:
            return stored
            
        if self.is_output:
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
    
    @layout.setter
    def layout(self, value):
        self._layout_value = value


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
