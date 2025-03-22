from email.policy import default
from typing import Literal, Set
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
    sn_nodes,
)
from scripting_nodes.src.lib.utils.sockets.sockets import (
    from_nodes,
    socket_index,
    to_nodes,
)
from scripting_nodes.src.lib.utils.screen.screen import redraw_all
from scripting_nodes.src.lib.utils.code.format import normalize_indents
from scripting_nodes.src.features.sockets.socket_types import SOCKET_IDNAME_TYPE
from scripting_nodes.src.lib.utils.uuid import get_short_id
from scripting_nodes.src.features.node_tree.node_tree import ScriptingNodeTree
import bpy


class ScriptingBaseNode:

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
    sn_reference_properties: Set[str] = set()

    id: bpy.props.StringProperty(
        default="", name="ID", description="Unique ID of the node"
    )

    code: bpy.props.StringProperty()
    code_global: bpy.props.StringProperty()

    ### Life Cycle

    def init(self, context: bpy.types.Context):
        """Called when the node is created"""
        self.on_create()
        self.id = get_short_id()
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
        if not self.id:
            return
        prev_code = (
            self.code
            + self.code_global
            + "".join([socket.code for socket in self.outputs])
        )
        # reset code
        self.code = ""
        self.code_global = ""
        for out in self.outputs:
            out.code = ""
        # generate new code
        self.generate()
        new_code = (
            self.code
            + self.code_global
            + "".join([socket.code for socket in self.outputs])
        )
        if prev_code != new_code:
            # propagate changes
            for out in self.outputs:
                for node in to_nodes(out):
                    node._generate()
            for inpt in self.inputs:
                for node in from_nodes(inpt):
                    node._generate()
            # mark node tree as dirty
            if "ROOT_NODE" in self.sn_options:
                self.node_tree.is_dirty = True
            redraw_all()
        # update references
        for ntree in scripting_node_trees():
            for node in sn_nodes(ntree):
                for prop in node.sn_reference_properties:
                    key = getattr(node, prop, "")
                    ref = bpy.context.scene.sna.references.get(key)
                    if ref and ref.node_id == self.id:
                        node.on_ref_change(self)

    def generate(self):
        raise NotImplementedError

    def _execute(self, globs, locs):
        exec(normalize_indents(self.code), globs, locs)

    ### Sockets

    def add_input(self, idname: SOCKET_IDNAME_TYPE, label="", dynamic=False):
        socket = self.inputs.new(idname, label)
        self._initialize_socket(socket, label, dynamic)
        return socket

    def add_output(self, idname: SOCKET_IDNAME_TYPE, label="", dynamic=False):
        socket = self.outputs.new(idname, label)
        self._initialize_socket(socket, label, dynamic)
        return socket

    def _initialize_socket(self, socket, label, dynamic):
        socket.name = label or socket.bl_label
        socket.display_shape = socket.socket_shape
        socket.is_dynamic = dynamic

    def ntree_link_created(self):
        self._update_dynamic_sockets()
        self._generate()

    def ntree_link_removed(self):
        self._generate()

    def _update_dynamic_sockets(self):
        # update inputs
        for socket in self.inputs:
            if socket.is_dynamic and socket.is_linked:
                index = socket_index(self, socket)
                self.add_input(socket.bl_idname, socket.label, dynamic=True)
                self.inputs.move(len(self.inputs) - 1, index + 1)
                socket.is_dynamic = False
                socket.is_removable = True
        # update outputs
        for socket in self.outputs:
            if socket.is_dynamic and socket.is_linked:
                index = socket_index(self, socket)
                self.add_output(socket.bl_idname, socket.label, dynamic=True)
                self.outputs.move(len(self.outputs) - 1, index + 1)
                socket.is_dynamic = False
                socket.is_removable = True

    def draw_buttons(self, context, layout):
        if bpy.context.scene.sna.dev.show_node_code:
            box = layout.box()
            for line in self.code.split("\n"):
                box.label(text=line)
        self.draw(context, layout)

    def draw(self, context, layout):
        pass
