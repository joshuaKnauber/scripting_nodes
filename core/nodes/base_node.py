import functools
import time

import bpy


from ..sockets.socket_ops import insert_dynamic_socket
from ..sockets.base_socket import ScriptingSocket
from ...core.node_tree.node_tree import ScriptingNodeTree
from ...core.nodes.utils.references import get_references_to_node
from ...core.utils.links import has_link_updates, revalidate_links
from ...core.utils.sockets import add_socket, convert_socket_type, is_last_with_name
from ...interface.overlays.nodes.node_overlays import set_node_error, set_node_time
from ...utils import logger
from ...utils.code import minimize_indents
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

    ### NODE PROPERTIES ###

    expand_internals: bpy.props.BoolProperty(
        default=False, name="Expand Internals", description="Expand internal properties"
    )

    pause_updates: bpy.props.BoolProperty(default=False, name="Pause Updates")

    ### NODE LIFE CYCLE ###

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
        refs = get_references_to_node(self)

        def update_refs():
            for ref in refs:
                ref.on_reference_update(None)

        bpy.app.timers.register(update_refs, first_interval=0.025)

    # Callback for when the node is deleted
    def on_delete(self):
        return

    def on_reference_update(self, node: bpy.types.Node):
        """Called on updates when a node is referenced by this node. Overrite this in nodes to handle updates"""
        self.mark_dirty()

    ### NODE SOCKETS ###

    def add_input(self, idname: str, name: str = "") -> ScriptingSocket:
        """Adds an input socket to the node"""
        return add_socket(self, idname, name, False)

    def add_output(self, idname: str, name: str = "") -> ScriptingSocket:
        """Adds an output socket to the node"""
        return add_socket(self, idname, name, True)

    def convert_socket(self, socket: ScriptingSocket, idname: str):
        """Converts a socket to another idname. Does not mark the node as dirty on its own"""
        self.pause_updates = True
        socket = convert_socket_type(socket, idname)
        self.pause_updates = False
        return socket

    def update(self):
        """Called by blender when the node topology changes"""
        # call link update functions
        if has_link_updates(self):
            self.update_links()
        # revalidate links
        bpy.app.timers.register(
            lambda: revalidate_links(self.node_tree), first_interval=0.025
        )

    def on_group_tree_update(self):
        """Called by the node tree when this nodes group_tree node tree updates"""

    def _add_dynamic_sockets(self):
        """Adds dynamic sockets if the last socket is linked"""
        for out in self.outputs:
            if out.dynamic and out.is_linked and is_last_with_name(self, out):
                insert_dynamic_socket(out, False)
        for inp in self.inputs:
            if inp.dynamic and inp.is_linked and is_last_with_name(self, inp):
                insert_dynamic_socket(inp, False)

    def update_links(self):
        """Called on link updates"""
        self._add_dynamic_sockets()
        self.mark_dirty()

    def _sockets_initialized(self):
        """Returns a boolean saying if all sockets are initialized"""
        for socket in [*self.inputs, *self.outputs]:
            if not socket.initialized:
                return False
        return True

    ### NODE CODE ###

    def _clean_code(self, code: str):
        """Cleans the code of the node"""
        return "\n".join([*filter(lambda l: l.strip() != "", code.split("\n"))])

    def get_code(self):
        return self.get("code", "")

    def set_code(self, value):
        self["code"] = self._clean_code(value)

    code: bpy.props.StringProperty(
        default="",
        name="Code",
        description="Generated code for the node",
        set=set_code,
        get=get_code,
    )

    def get_code_global(self):
        return self.get("code_global", "")

    def set_code_global(self, value):
        self["code_global"] = self._clean_code(value)

    code_global: bpy.props.StringProperty(
        default="",
        name="Code Global",
        description="Top level code for the node",
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
        self.code_global = ""
        self.code_register = ""
        self.code_unregister = ""
        self.require_register = False
        for inp in self.inputs:
            inp.reset_meta()
            inp.code = ""
        for out in self.outputs:
            out.reset_meta()
            out.code = ""

    def _get_code_summary(self):
        """Returns a summary of all the code stored in the node to check for changes"""
        code = self.code + self.code_global + self.code_register + self.code_unregister
        for socket in [*self.inputs, *self.outputs]:
            code += socket.meta
            code += socket.get_code()
        return code

    def generate(self, context: bpy.types.Context, trigger: bpy.types.Node):
        """Generates the code for the node. Overwrite this in nodes by setting the self.code... properties"""

    def mark_dirty(self, trigger: bpy.types.Node = None, retried: bool = False):
        """Called when the node changes. Forwards the update to the node tree if something has changed. Retries when the node is not ready"""
        if not self._sockets_initialized() or self.pause_updates:
            # retry when node not ready
            if not retried:
                self.mark_dirty_delayed(trigger)
            return
        # reset code
        summary = self._get_code_summary()
        self._reset_code()
        # generate new code
        try:
            self.generate(bpy.context, trigger if trigger else self)
        except Exception as e:
            logger.error(f"Error in node '{self.name}'", e)
        # check if code has changed
        if summary == self._get_code_summary():
            self._propagate_change_to_references()
            return
        # propagate changes and build addon if necessary
        self._start_was_registered()
        self._propagate_changes()
        # TODO when code_global and dev run the group node instead of rebuilding
        if self.require_register or self.code_global:
            self.node_tree.mark_dirty(self)

    def mark_dirty_delayed(self, trigger: bpy.types.Node = None):
        """Trigger mark dirty with a short delay"""
        bpy.app.timers.register(
            functools.partial(self.mark_dirty, trigger, True), first_interval=0.025
        )

    def _propagate_change_to_sockets(self):
        """Propagates the changes to the surrounding sockets"""
        for socket in [*self.inputs, *self.outputs]:
            if socket.has_next():
                for next in socket.get_next():
                    if hasattr(next.node, "mark_dirty"):
                        next.node.mark_dirty(self)

    def _propagate_change_to_references(self):
        """Propagates the changes to the surrounding and referencing nodes"""
        for ref in get_references_to_node(self):
            ref.on_reference_update(self)

    def _propagate_changes(self):
        """Propagates the changes to the surrounding and referencing nodes"""
        self._propagate_change_to_sockets()
        self._propagate_change_to_references()

    def _execute(self, local_vars: dict, global_vars: dict):
        """Executes the code for the node. Note that this code runs within the context of the running addon"""
        t1 = time.time()
        try:
            exec(minimize_indents(self.code), local_vars, global_vars)
            set_node_error(self.id, "")
        except Exception as e:
            logger.error(f"Error in node '{self.name}'")  # TODO
            set_node_error(self.id, str(e))
        set_node_time(self.id, (time.time() - t1) * 1000)

    ### Node UI ###

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
