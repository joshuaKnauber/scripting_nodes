import bpy

from ..lib.sockets import socket_index


class ScriptingBaseSocket(bpy.types.NodeSocket):
    """Base class for all Scripting Nodes sockets (not registered itself).

    Sockets hold no generated code. They describe a value (`literal()` is the
    Python expression of the socket's own value when nothing is connected)
    and draw themselves. Code is produced by the compiler (core/context.py).
    """

    # Prevent auto_load from registering this base class
    is_registered = True

    is_sn = True
    # Links only connect sockets of the same group: DATA, EXEC or INTERFACE
    socket_type = "DATA"
    socket_shape = "CIRCLE"
    color = (0.35, 0.35, 0.35, 1)

    # The trailing "+" socket of a dynamic socket group
    is_dynamic: bpy.props.BoolProperty(default=False)
    is_removable: bpy.props.BoolProperty(default=False)

    def literal(self) -> str:
        """Python expression of this socket's own value (when unconnected)."""
        return "None"

    def draw_value(self, context, layout, text):
        layout.label(text=text)

    def update_value(self, context):
        node = self.node
        if hasattr(node, "mark_dirty"):
            node.mark_dirty()
        else:  # Group Input / Output
            from ..core import scheduler

            scheduler.request_tree(node.id_data)

    def draw(self, context, layout, node, text):
        if self.is_dynamic:
            if self.is_output:
                layout.label(text=text)
            op = layout.operator(
                "sna.add_dynamic_socket", text="", icon="ADD", emboss=False
            )
            op.node_id = node.id
            op.socket_identifier = self.identifier
            op.is_output = self.is_output
            if not self.is_output:
                layout.label(text=text)
            return
        if self.is_removable and not self.is_output:
            op = layout.operator(
                "sna.remove_dynamic_socket", text="", icon="REMOVE", emboss=False
            )
            op.node_id = node.id
            op.socket_index = socket_index(node, self)
            op.is_output = False
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            self.draw_value(context, layout, text)
        if self.is_removable and self.is_output:
            op = layout.operator(
                "sna.remove_dynamic_socket", text="", icon="REMOVE", emboss=False
            )
            op.node_id = node.id
            op.socket_index = socket_index(node, self)
            op.is_output = True

    @classmethod
    def draw_color_simple(cls):
        return cls.color
