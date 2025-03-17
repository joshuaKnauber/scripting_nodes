from typing import Literal
from scripting_nodes.src.lib.utils.sockets.sockets import from_socket, to_socket
from scripting_nodes.src.lib.utils.code.format import normalize_indents
import bpy


class ScriptingBaseSocket(bpy.types.NodeSocket):

    is_sn = True
    socket_type: Literal["DATA", "PROGRAM"] = "DATA"
    socket_shape = "CIRCLE"

    code: bpy.props.StringProperty(default="")

    handles_dynamic_input: bpy.props.BoolProperty(default=False)
    add_socket_type: bpy.props.StringProperty(default="ScriptingDataSocket")
    add_socket_name: bpy.props.StringProperty(default="Item")
    last_connected_from_node: bpy.props.StringProperty(default="")
    last_connected_from_socket: bpy.props.StringProperty(default="")

    def eval(self, fallback=""):
        if self.socket_type == "PROGRAM":
            return self._eval_program() or fallback
        elif self.socket_type == "DATA":
            return self._eval_data() or fallback

    def _eval_program(self):
        if self.is_output:
            to = to_socket(self)
            if to:
                return to.eval()
            return ""
        else:
            if bpy.context.scene.sna.addon.build_with_production_code:
                return normalize_indents(self.node.code)
            else:
                return f"bpy.context.scene.sna.execute('{self.node.id}', globals(), locals())"

    def _eval_data(self):
        if self.is_output:
            return self.code
        else:
            from_s = from_socket(self)
            if from_s:
                return from_s.eval()
            return self._to_code()

    def _to_code(self):
        raise NotImplementedError

    def handle_dynamic_input(self):

        if not self.handles_dynamic_input:
            return False

        if not self.links:
            return False

        link = self.links[0]
        self.last_connected_from_node = link.from_node.name
        self.last_connected_from_socket = link.from_socket.name

        self.id_data.links.remove(link)

        new_socket = self.node.add_input(self.add_socket_type, self.add_socket_name)

        if hasattr(new_socket, "is_dynamic"):
            new_socket.is_dynamic = True

        for i, socket in enumerate(self.node.inputs):
            if socket == self:
                self.node.inputs.move(i, len(self.node.inputs) - 1)
                break

        from_node = self.id_data.nodes.get(self.last_connected_from_node)
        if from_node:
            from_socket = next(
                (
                    s
                    for s in from_node.outputs
                    if s.name == self.last_connected_from_socket
                ),
                None,
            )
            if from_socket:
                self.id_data.links.new(from_socket, new_socket)

        if hasattr(self.node, "on_socket_added"):
            self.node.on_socket_added(new_socket)

        return True
