from email.policy import default
from typing import Literal, Set
from scripting_nodes.src.lib.utils.screen.screen import redraw_all
from scripting_nodes.src.lib.utils.code.format import normalize_indents
from scripting_nodes.src.features.sockets.socket_types import SOCKET_IDNAMES
from scripting_nodes.src.lib.utils.uuid import get_short_id
from scripting_nodes.src.features.node_tree.node_tree import ScriptingNodeTree
import bpy


class ScriptingBaseNode(bpy.types.Node):

    @classmethod
    def poll(cls, ntree):
        """Checks if the node is valid"""
        return ntree.bl_idname == ScriptingNodeTree.bl_idname

    def ntree_poll(self, group):
        """Checks if the node tree is valid"""
        return group.bl_idname == ScriptingNodeTree.bl_idname

    @property
    def node_tree(self):
        """Returns the node tree this node lives in"""
        return self.id_data

    ### Properties

    is_sn = True

    sn_options: Set[Literal["ROOT_NODE"]] = {}

    id: bpy.props.StringProperty(
        default="", name="ID", description="Unique ID of the node"
    )

    code: bpy.props.StringProperty()

    ### Life Cycle

    def init(self, context: bpy.types.Context):
        """Called when the node is created"""
        self.id = get_short_id()
        self.on_create()
        self._generate()

    def on_create(self):
        pass

    def copy(self, node: bpy.types.Node):
        """Called when the node is copied"""
        self.id = get_short_id()
        self._generate()

    def free(self):
        """Called when the node is deleted"""
        self.node_tree.is_dirty = True

    ### Code Generation

    def _generate(self):
        prev_code = self.code + "".join([socket.code for socket in self.outputs])
        self.generate()
        new_code = self.code + "".join([socket.code for socket in self.outputs])
        if prev_code != new_code:
            # propagate changes
            for out in self.outputs:
                for link in out.links:
                    link.to_node._generate()
            for inpt in self.inputs:
                for link in inpt.links:
                    link.from_node._generate()
            # mark node tree as dirty
            if "ROOT_NODE" in self.sn_options:
                self.node_tree.is_dirty = True
            redraw_all()

    def generate(self):
        raise NotImplementedError

    def _execute(self, globals, locals):
        exec(normalize_indents(self.code), globals, locals)

    ### Sockets

    def add_input(self, idname: SOCKET_IDNAMES, label=""):
        socket = self.inputs.new(idname, label)
        self._initialize_socket(socket, label)
        return socket

    def add_output(self, idname: SOCKET_IDNAMES, label=""):
        socket = self.outputs.new(idname, label)
        self._initialize_socket(socket, label)
        return socket

    def _initialize_socket(self, socket, label):
        socket.name = label or socket.bl_label
        socket.display_shape = socket.socket_shape

    def ntree_link_created(self):
        self._generate()

    def ntree_link_removed(self):
        self._generate()

    def draw_buttons(self, context, layout):
        if bpy.context.scene.sna.dev.show_node_code:
            box = layout.box()
            for line in self.code.split("\n"):
                box.label(text=line)
        self.draw(context, layout)

    def draw(self, context, layout):
        pass
