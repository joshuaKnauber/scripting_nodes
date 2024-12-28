from typing import Literal
from scripting_nodes.src.lib.utils.code.format import normalize_indents
import bpy


class ScriptingBaseSocket(bpy.types.NodeSocket):

    is_sn = True
    socket_type: Literal["DATA", "PROGRAM"] = "DATA"
    socket_shape = "CIRCLE"

    code: bpy.props.StringProperty(default="")

    def eval(self, fallback=""):
        if self.socket_type == "PROGRAM":
            return self._eval_program() or fallback
        elif self.socket_type == "DATA":
            return self._eval_data() or fallback

    def _eval_program(self):
        if self.is_output:
            if len(self.links) > 0:
                return self.links[0].to_socket.eval()
            return ""
        else:
            return normalize_indents(self.node.code)

    def _eval_data(self):
        if self.is_output:
            return self.code
        else:
            if len(self.links) > 0:
                return self.links[0].from_socket.eval()
            return self._to_code()

    def _to_code(self):
        raise NotImplementedError


# Customizable interface properties to generate a socket from.
# class MyCustomInterfaceSocket(bpy.types.NodeTreeInterfaceSocket):
#     # The type of socket that is generated.
#     bl_socket_idname = "CustomSocketType"

#     default_value: bpy.props.FloatProperty(
#         default=1.0,
#         description="Default input value for new sockets",
#     )

#     def draw(self, context, layout):
#         # Display properties of the interface.
#         layout.prop(self, "default_value")

#     # Set properties of newly created sockets
#     def init_socket(self, node, socket, data_path):
#         socket.input_value = self.default_value

#     # Use an existing socket to initialize the group interface
#     def from_socket(self, node, socket):
#         # Current value of the socket becomes the default
#         self.default_value = socket.input_value
