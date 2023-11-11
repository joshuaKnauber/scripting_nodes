import time

import bpy

from ...core.node_tree.node_tree import ScriptingNodesTree
from ...core.nodes.utils.references import NodePointer, get_references_to_node
from ...core.utils.links import handle_link_insert, handle_link_remove, is_link_valid
from ...core.utils.sockets import add_socket
from ...interface.overlays.nodes.node_overlays import set_node_error, set_node_time
from ...utils import logger
from ...utils.code import normalize_indents
from ..utils.id import get_id
from .utils.draw_code import draw_code


class SN_BaseNode(bpy.types.Node):
    is_sn = True
    bl_label = "Base Node"

    id: bpy.props.StringProperty(default="", name="ID", description="Unique ID of the node")

    @classmethod
    def poll(cls, ntree):
        """ Checks if the node is valid """
        return ntree.bl_idname == ScriptingNodesTree.bl_idname

    def ntree_poll(self, group):
        """ Checks if the node tree is valid """
        return group.bl_idname == ScriptingNodesTree.bl_idname

    @property
    def node_tree(self):
        """Returns the node tree this node lives in"""
        return self.id_data

    def init(self, context: bpy.types.Context):
        """ Called when the node is created """
        sn = bpy.context.scene.sn
        self.id = get_id()
        sn.references.add_reference(self)
        self.on_create()
        self.mark_dirty()

    # Callback for when the node is created
    def on_create(self): return

    def copy(self, node: bpy.types.Node):
        """ Called when the node is copied """
        sn = bpy.context.scene.sn
        self.id = get_id()
        sn.references.add_reference(self)
        self.on_copy(node)
        self.mark_dirty()

    # Callback for when the node is copied
    def on_copy(self, node: bpy.types.Node): return

    def free(self):
        """ Called when the node is deleted """
        sn = bpy.context.scene.sn
        self.on_delete()
        sn.references.remove_reference(self)
        self.node_tree.mark_dirty(self)

    # Callback for when the node is deleted
    def on_delete(self): return

    def add_input(self, idname: str, name: str = ""):
        """ Adds an input socket to the node """
        return add_socket(self, idname, name, False)

    def add_output(self, idname: str, name: str = ""):
        """ Adds an output socket to the node """
        return add_socket(self, idname, name, True)

    def insert_link(self, link: bpy.types.NodeLink):
        """ Called when a link is inserted """
        # handle_link_insert(self, link)
        pass  # TODO are these necessary

    def remove_link(self, link: bpy.types.NodeLink):
        """ Called when a link is removed """
        print("link removed", self)
        # handle_link_remove(self, link)

    def update(self):
        """ Called by blender when the node topology changes """
        # handle_link_updates(self) # TODO
        self.mark_dirty()  # TEMP

    code: bpy.props.StringProperty(default="", name="Code", description="Generated code for the node")
    code_register: bpy.props.StringProperty(default="", name="Code Register", description="Generated register code for the node")
    code_unregister: bpy.props.StringProperty(default="", name="Code Unregister", description="Generated unregister code for the node")

    require_register: bpy.props.BoolProperty(default=False, name="Require Register", description="If an update to this node needs to trigger a reregister")

    def _reset_code(self):
        self.code = ""
        self.code_register = ""
        self.code_unregister = ""
        self.require_register = False
        for inp in self.inputs:
            inp.reset_meta()
        for out in self.outputs:
            out.reset_meta()

    def _get_code_summary(self):
        """ Returns a summary of all the code stored in the node to check for changes """
        code = self.code + self.code_register + self.code_unregister
        for socket in [*self.inputs, *self.outputs]:
            code += socket.meta
            code += socket.get_code()
        return code

    def generate(self, context: bpy.types.Context):
        """ Generates the code for the node. Overwrite this in nodes by setting the self.code... properties """

    def on_reference_update(self, node: bpy.types.Node):
        """ Called when a node is referenced by this node """

    def mark_dirty(self):
        """ Called when the node changes. Forwards the update to the node tree """
        summary = self._get_code_summary()
        self._reset_code()
        self.generate(bpy.context)
        if summary == self._get_code_summary():
            return
        self._propagate_changes()
        if self.require_register:
            self.node_tree.mark_dirty(self)

    def _propagate_changes(self):
        """ Propagates the changes to the surrounding and referencing nodes """

        def propagate_change_to_sockets(self):
            for socket in [*self.inputs, *self.outputs]:
                if socket.has_next():
                    for next in socket.get_next():
                        next.node.mark_dirty()

        def propagate_change_to_references(self):
            for ref in get_references_to_node(self):
                ref.on_reference_update(self)

        propagate_change_to_sockets(self)
        propagate_change_to_references(self)

    def _execute(self, local_vars: dict, global_vars: dict):
        """ Executes the code for the node. Note that this code runs within the context of the running addon """
        t1 = time.time()
        try:
            exec(normalize_indents(self.code), local_vars, global_vars)
            set_node_error(self.id, "")
        except Exception as e:
            logger.error(f"Error in node '{self.name}'")  # TODO
            set_node_error(self.id, str(e))
        set_node_time(self.id, (time.time() - t1)*1000)

    def draw_buttons(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        """ Draws the buttons on the node """
        sn = context.scene.sn
        if self.select and sn.show_node_code:
            draw_code(layout, self)
        self.draw_node(context, layout)

    # Callback for when the node is drawn
    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout): return
