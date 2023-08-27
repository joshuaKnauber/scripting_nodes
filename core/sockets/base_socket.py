import json

import bpy

from ..utils import sockets


class ScriptingSocket:
    is_sn = True

    initialized: bpy.props.BoolProperty(default=False)

    draw_output_value: bpy.props.BoolProperty(default=False, name="Draw Output Value", description="Draw the value of the socket event if it is an output")
    draw_linked_value: bpy.props.BoolProperty(default=False, name="Draw Linked Value", description="Draw the value of the socket even if it is linked")

    def __init__(self):
        if not self.initialized:
            self.init()
            self.initialized = True

    def init(self):
        self.on_create(bpy.context)

    # callback for when the socket is created
    def on_create(self, context): return

    def draw(self, context, layout, node, text):
        self.draw_socket(context, layout, node, text, self.draw_linked_value, self.draw_output_value)

    # callback for drawing the socket
    def draw_socket(self, context, layout, node, text, draw_linked_value, draw_output_value):
        raise NotImplementedError

    def draw_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return self.get_color(context, node)

    def get_color(self, context, node):
        raise NotImplementedError

    def has_next(self) -> bool:
        """ Returns a boolean saying if the node is connected to other valid sockets """
        return len(sockets.get_next_sockets(self)) > 0

    def get_next(self) -> list[bpy.types.NodeSocket]:
        """ Returns a list of all valid connected sockets """
        return sockets.get_next_sockets(self)

    def value_code(self):
        raise NotImplementedError

    def code(self, indent: int = 0, fallback: str = ""):
        if self.is_output:
            if not self.has_next():
                return fallback
            ntree = self.node.node_tree
            return f"bpy.data.node_groups['{ntree.name}']._execute_node('{self.get_next()[0].node.id}', locals(), globals())\n"
        else:
            if self.has_next():
                return self.get_next()[0].value_code()
            return self.value_code()

    meta: bpy.props.StringProperty(default="{}", name="Metadata", description="Stringified JSON metadata passed along by this socket")

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
