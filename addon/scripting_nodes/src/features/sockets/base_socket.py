from typing import Literal
from scripting_nodes.src.lib.utils.sockets.sockets import from_socket, to_socket
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
