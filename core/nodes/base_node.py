import functools
import time

import bpy

from ...core.node_tree.node_tree import ScriptingNodeTree
from ...core.nodes.utils.references import get_references_to_node
from ...core.utils.links import has_link_updates, revalidate_links
from ...core.utils.sockets import add_socket
from ...interface.overlays.nodes.node_overlays import set_node_error, set_node_time
from ...utils import logger
from ...utils.code import normalize_indents
from ...utils import redraw
from ..utils.id import get_id
from .utils.draw_code import draw_code


_LAST_UPDATED = set()  # set of node ids that have recently been updated


class SNA_BaseNode(bpy.types.Node):
    is_sn_node = True
    bl_label = "Base Node"

    id: bpy.props.StringProperty(
        default="", name="ID", description="Unique ID of the node"
    )

    def _start_was_registered(self):
        global _LAST_UPDATED
        _LAST_UPDATED.add(self.id)
        redraw.redraw(True)
        bpy.app.timers.register(
            functools.partial(self._finish_was_registered, self.id), first_interval=1
        )

    def _finish_was_registered(self, id):
        global _LAST_UPDATED
        if id in _LAST_UPDATED:
            _LAST_UPDATED.remove(id)
        redraw.redraw(True)

    expand_internals: bpy.props.BoolProperty(
        default=False, name="Expand Internals", description="Expand internal properties"
    )

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

    def init(self, context: bpy.types.Context):
        """Called when the node is created"""
        sna = bpy.context.scene.sna
        self.id = get_id()
        sna.references.add_reference(self)
        self.on_create()
        self.mark_dirty()

    # Callback for when the node is created
    def on_create(self):
        return

    def copy(self, node: bpy.types.Node):
        """Called when the node is copied"""
        sna = bpy.context.scene.sna
        self.id = get_id()
        sna.references.add_reference(self)
        self.on_copy(node)
        self.mark_dirty()

    # Callback for when the node is copied
    def on_copy(self, node: bpy.types.Node):
        return

    def free(self):
        """Called when the node is deleted"""
        sna = bpy.context.scene.sna
        self.on_delete()
        sna.references.remove_reference(self)
        self.node_tree.mark_dirty(self)

    # Callback for when the node is deleted
    def on_delete(self):
        return

    def add_input(self, idname: str, name: str = ""):
        """Adds an input socket to the node"""
        return add_socket(self, idname, name, False)

    def add_output(self, idname: str, name: str = ""):
        """Adds an output socket to the node"""
        return add_socket(self, idname, name, True)

    def update(self):
        """Called by blender when the node topology changes"""
        if has_link_updates(self):
            self.update_links()

    def update_links(self):
        """Called on link updates"""
        self.mark_dirty()
        bpy.app.timers.register(
            lambda: revalidate_links(self.node_tree), first_interval=0.025
        )

    code: bpy.props.StringProperty(
        default="", name="Code", description="Generated code for the node"
    )
    code_register: bpy.props.StringProperty(
        default="",
        name="Code Register",
        description="Generated register code for the node",
    )
    code_unregister: bpy.props.StringProperty(
        default="",
        name="Code Unregister",
        description="Generated unregister code for the node",
    )

    require_register: bpy.props.BoolProperty(
        default=False,
        name="Require Register",
        description="If an update to this node needs to trigger a reregister",
    )

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
        """Returns a summary of all the code stored in the node to check for changes"""
        code = self.code + self.code_register + self.code_unregister
        for socket in [*self.inputs, *self.outputs]:
            code += socket.meta
            code += socket.get_code()
        return code

    def generate(self, context: bpy.types.Context):
        """Generates the code for the node. Overwrite this in nodes by setting the self.code... properties"""

    def on_reference_update(self, node: bpy.types.Node):
        """Called on updates when a node is referenced by this node. Overrite this in nodes to handle updates"""
        self.mark_dirty()

    def mark_dirty(self):
        """Called when the node changes. Forwards the update to the node tree if something has changed"""
        summary = self._get_code_summary()
        self._reset_code()
        self.generate(bpy.context)
        if summary == self._get_code_summary():
            return
        self._start_was_registered()
        self._propagate_changes()
        if self.require_register:
            self.node_tree.mark_dirty(self)

    def _propagate_changes(self):
        """Propagates the changes to the surrounding and referencing nodes"""

        def propagate_change_to_sockets(self):
            for socket in [*self.inputs, *self.outputs]:
                if socket.has_next():
                    for next in socket.get_next():
                        # if not getattr(next, "is_program", False):
                        next.node.mark_dirty()

        def propagate_change_to_references(self):
            for ref in get_references_to_node(self):
                ref.on_reference_update(self)

        propagate_change_to_sockets(self)
        propagate_change_to_references(self)

    def _execute(self, local_vars: dict, global_vars: dict):
        """Executes the code for the node. Note that this code runs within the context of the running addon"""
        t1 = time.time()
        try:
            exec(normalize_indents(self.code), local_vars, global_vars)
            set_node_error(self.id, "")
        except Exception as e:
            logger.error(f"Error in node '{self.name}'")  # TODO
            set_node_error(self.id, str(e))
        set_node_time(self.id, (time.time() - t1) * 1000)

    def draw_buttons(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        """Draws the buttons on the node"""
        global _LAST_UPDATED
        if self.id in _LAST_UPDATED and context.scene.sna.show_register_updates:
            layout.progress(
                text="Updating...",
                factor=0.5,
            )
        sna = context.scene.sna
        if self.select and sna.show_node_code:
            draw_code(layout, self)
        self.draw_node(context, layout)

    # Callback for when the node is drawn
    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        return
