import bpy
from ...utils.logging import log


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

    def _format_code_value(self, value):
        """ Formats multiline code values to be indented correctly. """
        if "\n" in value:
            lines = value.split("\n")
            # remove empty lines
            lines = [*filter(lambda line: line.strip() != "", lines)]
            lines = [*map(lambda line: line.rstrip(), lines)]
            # remove indent
            min_indent = min([len(line) - len(line.lstrip())
                             for line in lines])
            lines = [line[min_indent:] for line in lines]
            value = "\n".join(lines)
        return value

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
        return self["code"] if "code" in self else ""

    def set_code(self, value):
        """ Formats and sets the code for this socket. Updates connected nodes if necessary. """
        value = self._format_code_value(value)
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

    def code_block(self, indents=0):
        """ Returns the code block for this socket. Indents multiline code values by the given amount. """
        return "\n".join([" "*4 * indents * min(i, 1) + line for i, line in enumerate(self.code.split("\n"))])
