import bpy


class ScriptingSocket:
    is_sn = True

    initialized: bpy.props.BoolProperty(default=False)

    def __init__(self):
        if not self.initialized:
            self.init()
            self.initialized = True

    def init(self):
        self.on_create(bpy.context)

    def on_create(self, context):  # callback for when the socket is created
        raise NotImplementedError

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return self.get_color(context, node)

    def get_color(self, context, node):
        raise NotImplementedError

    def code(self, indent: int = 0, fallback: str = ""):
        if not self.is_output or len(self.links) == 0:
            return fallback
        ntree = self.node.node_tree
        to_socket = self.links[0].to_socket
        return f"bpy.data.node_groups['{ntree.name}'].nodes['{to_socket.node.name}']._execute(locals(), globals())"
