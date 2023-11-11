import json

import bpy

from ..utils import sockets
from .data.convert import convert_types


class ScriptingSocket:
    is_sn = True

    initialized: bpy.props.BoolProperty(default=False)

    enabled: bpy.props.BoolProperty(default=True, name="Enabled", description="Enable or disable this socket", update=lambda self, _: self.node.mark_dirty())
    show_enable: bpy.props.BoolProperty(default=False, name="Show Enabled", description="Show the enable icon")

    def __init__(self):
        if not self.initialized:
            self.init()
            self.initialized = True

    def init(self):
        self.on_create(bpy.context)

    # callback for when the socket is created
    def on_create(self, context): return

    def draw(self, context, layout, node, text):
        self.draw_socket(context, layout, node, text)

    # callback for drawing the socket
    def draw_socket(self, context, layout, node, text):
        raise NotImplementedError

    @classmethod
    def draw_color_simple(cls):
        return cls.get_color(None, None, None)

    def draw_color(self, context: bpy.types.Context, node: bpy.types.Node):
        # TODO I guess this doesn't exist anymore?
        return self.get_color(context, node)

    def get_color(self, context, node):
        raise NotImplementedError

    def has_next(self) -> bool:
        """ Returns a boolean saying if the node is connected to other valid sockets """
        return len(sockets.get_next_sockets(self)) > 0

    def get_next(self) -> list[bpy.types.NodeSocket]:
        """ Returns a list of all valid connected sockets """
        return sockets.get_next_sockets(self)

    def _python_value(self):
        raise NotImplementedError

    code: bpy.props.StringProperty(default="", name="Code", description="The code returned by this socket")

    def get_code(self, indent: int = 0, fallback: str = ""):
        if self.is_output:
            if getattr(self, "is_program", False):
                if not self.has_next():
                    return fallback
                ntree = self.node.node_tree
                return f"bpy.context.scene.sn._execute_node('{ntree.id}', '{self.get_next()[0].node.id}', locals(), globals())\n"
            else:
                return self._python_value()
        elif not getattr(self, "is_program", False):
            if self.has_next():
                from_socket = self.get_next()[0]
                return convert_types(from_socket._python_value(), from_socket, self)
            return self._python_value()
        return fallback

    meta: bpy.props.StringProperty(default="{}", name="Metadata", description="Stringified JSON metadata passed along by this socket")

    def reset_meta(self):
        self.meta = "{}"

    def set_meta(self, key: str, value):
        meta = json.loads(self.meta)
        meta[key] = value
        self.meta = json.dumps(meta)

    def get_meta(self, key: str, fallback):
        if not self.is_output:
            if self.has_next():
                return self.get_next()[0].get_meta(key, fallback)
            return fallback
        meta = json.loads(self.meta)
        if key in meta:
            return meta[key]
        return fallback
