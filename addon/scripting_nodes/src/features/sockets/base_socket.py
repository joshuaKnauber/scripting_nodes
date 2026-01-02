from typing import Literal, Set
from ...lib.utils.sockets.sockets import (
    from_socket,
    socket_index,
    to_socket,
)
from ...lib.utils.code.format import normalize_indents
from .conversions import get_conversion
import bpy

# Thread-local set to track sockets currently being evaluated (recursion guard)
_eval_stack: Set[str] = set()


class ScriptingBaseSocket(bpy.types.NodeSocket):
    """Base class for all scripting node sockets.

    Not registered as a Blender type - subclasses are registered instead.
    """

    # Prevent auto_load from registering this base class
    is_registered = True

    is_sn = True
    socket_type: Literal["DATA", "PROGRAM"] = "DATA"
    socket_shape = "CIRCLE"

    code: bpy.props.StringProperty(default="")

    is_dynamic: bpy.props.BoolProperty(default=False)
    is_removable: bpy.props.BoolProperty(default=False)

    def _get_socket_id(self):
        """Get a unique ID for this socket to detect recursion."""
        return f"{self.node.id}:{self.name}:{self.is_output}"

    def eval(self, fallback=""):
        # Recursion guard - prevent infinite loops
        socket_id = self._get_socket_id()
        if socket_id in _eval_stack:
            return fallback

        _eval_stack.add(socket_id)
        try:
            if self.socket_type == "PROGRAM":
                return self._eval_program() or fallback
            elif self.socket_type == "DATA":
                return self._eval_data() or fallback
        finally:
            _eval_stack.discard(socket_id)

    def _eval_program(self):
        if self.is_output:
            to = to_socket(self)
            if to:
                return to.eval()
            return ""
        else:
            # Group trees must always use production code because
            # return statements don't work with exec() in dev mode
            is_group_tree = getattr(self.node.node_tree, "is_group", False)
            if bpy.context.scene.sna.addon.build_with_production_code or is_group_tree:
                return normalize_indents(self.node.code)
            else:
                return f"bpy.context.scene.sna.execute('{self.node.id}', globals(), locals())"

    def _eval_data(self):
        if self.is_output:
            return self.code
        else:
            from_s = from_socket(self)
            if from_s:
                # Apply type conversion if connected socket is a different type
                value_code = from_s.eval()
                return get_conversion(from_s.bl_idname, self.bl_idname, value_code)
            return self._to_code()

    def _to_code(self):
        raise NotImplementedError

    def draw_socket(self, context, layout, node, text):
        raise NotImplementedError

    def draw(self, context, layout, node, text):
        # dynamic socket UI
        if self.is_output and (self.is_dynamic or self.is_removable):
            if self.is_dynamic:
                layout.label(text=text)
                op = layout.operator(
                    "sna.add_dynamic_socket", text="", icon="ADD", emboss=False
                )
                op.node_id = node.id
                op.socket_label = self.label
                op.is_output = self.is_output
            elif self.is_removable:
                op = layout.operator(
                    "sna.remove_dynamic_socket",
                    text="",
                    icon="REMOVE",
                    emboss=False,
                )
                op.node_id = node.id
                op.socket_index = socket_index(node, self)
                op.is_output = self.is_output

        # dynamic socket UI
        if not self.is_output and self.is_removable:
            if self.is_removable:
                op = layout.operator(
                    "sna.remove_dynamic_socket", text="", icon="REMOVE", emboss=False
                )
                op.node_id = node.id
                op.socket_index = socket_index(node, self)
                op.is_output = self.is_output

        # normal socket UI
        if not self.is_dynamic:
            self.draw_socket(context, layout, node, text)

        # dynamic socket UI
        if not self.is_output and self.is_dynamic:
            op = layout.operator(
                "sna.add_dynamic_socket", text="", icon="ADD", emboss=False
            )
            op.node_id = node.id
            op.socket_label = self.label
            op.is_output = self.is_output
            layout.label(text=text)
