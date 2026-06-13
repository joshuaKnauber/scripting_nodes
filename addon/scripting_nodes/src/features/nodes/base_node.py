from typing import Dict, Literal, Set, Tuple
from ...lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
    sn_nodes,
)
from ...lib.utils.sockets.sockets import (
    from_nodes,
    socket_index,
    to_nodes,
)
from ...lib.utils.screen.screen import redraw_all
from ..sockets.socket_types import SOCKET_IDNAME_TYPE
from ...lib.utils.uuid import get_short_id
from ..node_tree.node_tree import ScriptingNodeTree
from ..node_tree.code_gen.watcher import watch_changes
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
    # {prop_name: tuple-of-allowed-bl_idnames}. Each entry declares a string
    # reference field on the node, plus which node types are valid targets.
    # Discovery in settings_properties uses these tuples to create one
    # CollectionProperty per unique signature on scene.sna, so prop_search
    # dropdowns only show the relevant nodes.
    sn_reference_properties: Dict[str, Tuple[str, ...]] = {}
    # PointerProperty fields whose value is another ScriptingNodeTree. Used by
    # the dependency tracker to know "this node depends on that tree's file".
    sn_tree_reference_properties: Set[str] = set()

    id: bpy.props.StringProperty(
        default="", name="ID", description="Unique ID of the node"
    )

    code_imports: bpy.props.StringProperty()
    code_module: bpy.props.StringProperty()
    code_inline: bpy.props.StringProperty()
    code_global: bpy.props.StringProperty()
    code_register: bpy.props.StringProperty()
    code_unregister: bpy.props.StringProperty()

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
            self.code_imports
            + self.code_module
            + self.code_inline
            + self.code_global
            + self.code_register
            + self.code_unregister
            + "".join(
                [socket.code for socket in self.outputs if hasattr(socket, "code")]
            )
        )
        # reset code
        self.code_imports = ""
        self.code_module = ""
        self.code_inline = ""
        self.code_global = ""
        self.code_register = ""
        self.code_unregister = ""
        for out in self.outputs:
            if hasattr(out, "code"):
                out.code = ""
        # Skip generation if any sockets are not custom sockets (e.g. during reroute operations)
        for socket in list(self.inputs) + list(self.outputs):
            if not hasattr(socket, "eval"):
                return
        # generate new code
        self.generate()
        new_code = (
            self.code_imports
            + self.code_module
            + self.code_inline
            + self.code_global
            + self.code_register
            + self.code_unregister
            + "".join(
                [socket.code for socket in self.outputs if hasattr(socket, "code")]
            )
        )
        if prev_code != new_code:
            # propagate changes - cycles are prevented at link creation, so
            # this naturally terminates via the prev_code != new_code check
            for out in self.outputs:
                for node in to_nodes(out):
                    node._generate()
            for inpt in self.inputs:
                for node in from_nodes(inpt):
                    node._generate()
            # mark node tree as dirty if this node contributes to the file's
            # written content (root code, register/unregister, imports, globals).
            # For group trees, ANY node change can affect the emitted function
            # body, so mark dirty unconditionally.
            if (
                "ROOT_NODE" in self.sn_options
                or self.code_register
                or self.code_unregister
                or self.code_imports
                or self.code_global
                or getattr(self.node_tree, "is_group", False)
            ):
                self.node_tree.is_dirty = True
                # Trigger immediate regeneration to avoid stale file on redraw
                watch_changes()
            redraw_all()
        # Keep refs membership in sync. update_node_references() fires only
        # on link edits (NodeTree.update() doesn't fire on bare node add), so
        # a freshly added/duplicated node would never land in refs until the
        # user happens to make a link. Self-heal here so the picker dropdowns
        # see new nodes immediately. Self lands in every signature-collection
        # whose filter accepts this node's bl_idname.
        from ..settings.settings_properties import (
            collections_for_bl_idname,
            signature_key,
        )
        new_ref_name = f"{self.name} ({self.node_tree.name})"
        for coll in collections_for_bl_idname(self.bl_idname):
            for ref in coll:
                if ref.node_id == self.id:
                    if ref.name != new_ref_name:
                        ref.name = new_ref_name
                    break
            else:
                ref = coll.add()
                ref.name = new_ref_name
                ref.node_id = self.id

        # notify referencing nodes
        settings = bpy.context.scene.sna
        for ntree in scripting_node_trees():
            for node in sn_nodes(ntree):
                for prop in node.sn_reference_properties:
                    key = getattr(node, prop, "")
                    if not key:
                        continue
                    coll = getattr(settings, node._ref_collection_attr(prop))
                    ref = coll.get(key)
                    if ref and ref.node_id == self.id:
                        node.on_ref_change(self)
                # Container nodes hold refs in a CollectionProperty - notify
                # them when one of their attached properties changes signature
                cb_entries = getattr(node, "class_body_properties", None)
                cb_sig = getattr(node, "sn_class_body_signature", ())
                if cb_entries is not None and cb_sig:
                    coll = getattr(settings, signature_key(cb_sig))
                    for entry in cb_entries:
                        if not entry.prop:
                            continue
                        ref = coll.get(entry.prop)
                        if ref and ref.node_id == self.id:
                            node._generate()
                            break

    def generate(self):
        raise NotImplementedError

    ### Reference helpers

    @classmethod
    def _ref_collection_attr(cls, prop_name):
        """scene.sna attribute name of the collection backing this ref-property."""
        from ..settings.settings_properties import signature_key
        return signature_key(cls.sn_reference_properties[prop_name])

    def resolve_reference(self, prop_name):
        """Return the node a reference-property points to, or None."""
        coll = getattr(bpy.context.scene.sna, self._ref_collection_attr(prop_name))
        ref = coll.get(getattr(self, prop_name, ""))
        return ref.node if ref else None

    def draw_reference_prop(self, layout, prop_name, text=""):
        """Standard UI for picking another SN node by reference."""
        layout.prop_search(
            self,
            prop_name,
            bpy.context.scene.sna,
            self._ref_collection_attr(prop_name),
            text=text,
        )

    def reference_is_cross_tree(self, prop_name):
        """True iff the referenced node lives in a different tree."""
        target = self.resolve_reference(prop_name)
        return target is not None and target.id_data is not self.node_tree

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
            # Only check is_dynamic on our custom sockets
            if hasattr(socket, "is_dynamic") and socket.is_dynamic and socket.is_linked:
                index = socket_index(self, socket)
                self.add_input(socket.bl_idname, socket.label, dynamic=True)
                self.inputs.move(len(self.inputs) - 1, index + 1)
                socket.is_dynamic = False
                socket.is_removable = True
        # update outputs
        for socket in self.outputs:
            # Only check is_dynamic on our custom sockets
            if hasattr(socket, "is_dynamic") and socket.is_dynamic and socket.is_linked:
                index = socket_index(self, socket)
                self.add_output(socket.bl_idname, socket.label, dynamic=True)
                self.outputs.move(len(self.outputs) - 1, index + 1)
                socket.is_dynamic = False
                socket.is_removable = True

    def draw_buttons(self, context, layout):
        if bpy.context.scene.sna.dev.show_node_code:
            box = layout.box()
            shown = self.code_module or self.code_inline
            for line in shown.split("\n"):
                box.label(text=line)
        self.draw(context, layout)

    def draw(self, context, layout):
        pass
