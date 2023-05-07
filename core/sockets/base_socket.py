import bpy


class ScriptingSocket:
    is_sn = True
    is_program = False

    ### INITIALIZE
    initialized: bpy.props.BoolProperty(default=False)

    def __init__(self):
        if not self.initialized:
            self.init()
            self.initialized = True

    def on_create(self, context):
        pass

    def init(self):
        self.on_create(bpy.context)

    ### DRAW
    def draw_socket(self, context, layout, node, text):
        return False

    def draw(self, context, layout, node, text):
        if not self.draw_socket(context, layout, node, text):
            layout.label(text=text)

    def get_color(self, context, node):
        raise NotImplementedError

    def draw_color(self, context, node):
        color = self.get_color(context, node)
        if len(color) == 3:
            return color + (1,)
        return color
