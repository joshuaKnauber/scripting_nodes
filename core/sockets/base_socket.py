import bpy
from ...utils.logging import log
from ...utils.code_generation import cleanup_code


class ScriptingSocket:
    is_sn = True
    is_program = False

    # UTILS
    @property
    def node_tree(self):
        return self.node.node_tree

    @property
    def connected_nodes(self):
        if self.is_output:
            return [link.to_node for link in self.links]
        return [link.from_node for link in self.links]

    @property
    def connected_sockets(self):
        # TODO handle reroutes
        if self.is_output:
            return [link.to_socket for link in self.links]
        return [link.from_socket for link in self.links]

    @property
    def next(self):
        connected = self.connected_sockets
        if len(connected) == 0:
            return None
        if self.is_program:
            return connected[0]
        return connected

    @property
    def index(self):
        if self.is_output:
            return [*self.node.outputs].index(self)
        return [*self.node.inputs].index(self)

    # INITIALIZE
    initialized: bpy.props.BoolProperty(default=False)

    def __init__(self):
        if not self.initialized:
            self.init()
            self.initialized = True

    def on_create(self, context):
        pass

    def init(self):
        self.on_create(bpy.context)

    # DRAW
    def draw_socket(self, context, layout, node, text):
        return False

    def draw(self, context, layout, node, text):
        if self.draw_socket(context, layout, node, text) is False:
            layout.label(text=text)

    def get_color(self, context, node):
        raise NotImplementedError

    def draw_color(self, context, node):
        color = self.get_color(context, node)
        if len(color) == 3:
            return color + (1,)
        return color

    # CODE

    def get_code(self):
        """ Returns the code for this socket. """
        # return code from connected node for program outputs
        if self.is_program and self.is_output:
            next = self.next
            return next.code if next else ""
        # return code from connected node or own value for data inputs
        elif not self.is_program and not self.is_output:
            next = self.next
            return next[0].code if next else self.value_code
        return self["code"].strip() if "code" in self else ""

    def set_code(self, value):
        """ Formats and sets the code for this socket. Updates connected nodes if necessary. """
        value = cleanup_code(value)
        is_dirty = self.get_code() != value
        self["code"] = value
        if is_dirty and self.is_linked:  # add connected node to queue
            for node in self.connected_nodes:
                log(0, f"Adding {node.name} to queue after update on {'output' if self.is_output else 'input'} {self.index} from {self.node.name}")
                self.node_tree.add_to_queue(node)

    code: bpy.props.StringProperty(default="", get=get_code, set=set_code)

    @property
    def value_code(self):
        """ Returns the code value for this data socket. """
        if not self.is_program:
            raise NotImplementedError

    def code_block(self, indents=0, default=""):
        """ Returns the code block for this socket. Indents multiline code values by the given amount. """
        code = "\n".join([" "*4 * indents * min(i, 1) + line for i,
                         line in enumerate(self.code.split("\n"))]).strip()
        return code if code != "" else default
