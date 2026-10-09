from typing import Dict, Tuple

import bpy

from ..core import errors, scheduler
from ..core.references import find_node, install_reference_properties, ref_id_key
from ..lib.ids import get_short_id
from ..node_tree.node_tree import ScriptingNodeTree
from ..sockets.spec import MISSING, SocketSpec

# Property types whose changes regenerate code automatically
_AUTO_UPDATE_PROPS = {
    "BoolProperty",
    "IntProperty",
    "FloatProperty",
    "StringProperty",
    "EnumProperty",
    "BoolVectorProperty",
    "IntVectorProperty",
    "FloatVectorProperty",
    "PointerProperty",
}


def _auto_update(self, context):
    self.mark_dirty()


def _install_auto_updates(cls):
    """Every node property regenerates code when changed - no update= needed."""
    for base in cls.__mro__:
        if base.__module__.startswith("bpy"):
            continue
        annotations = base.__dict__.get("__annotations__", {})
        for name, prop in list(annotations.items()):
            function = getattr(prop, "function", None)
            keywords = getattr(prop, "keywords", None)
            if function is None or keywords is None:
                continue
            if function.__name__ not in _AUTO_UPDATE_PROPS:
                continue
            if "update" in keywords or "get" in keywords or "set" in keywords:
                continue
            annotations[name] = function(**keywords, update=_auto_update)


class ScriptingBaseNode:
    """Base class of every Scripting Nodes node.

    A node declares its sockets (`sn_inputs` / `sn_outputs`, see sockets/spec)
    and writes code in `emit(ctx)` (see core/context.py). Nodes store no
    generated code: the compiler calls `emit` whenever the addon is rebuilt.
    """

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == ScriptingNodeTree.bl_idname

    is_sn = True

    # -- declaration ----------------------------------------------------------

    sn_inputs: list = []
    sn_outputs: list = []
    # Root nodes are emitted on their own (operators, panels, events, ...).
    # Other nodes are emitted when a flow reaches them or a value is used.
    sn_root = False
    # Order of root nodes in the module (lower first). Classes other roots
    # reference at definition time (PropertyGroups) need to come first.
    sn_order = 50
    # Properties drawn on the node before `draw()`
    sn_header_props: Tuple[str, ...] = ()
    # {prop_name: allowed bl_idnames}: string fields referencing other nodes,
    # stored by node id (core/references.py)
    sn_reference_properties: Dict[str, Tuple[str, ...]] = {}

    id: bpy.props.StringProperty(default="", options={"HIDDEN"})

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _install_auto_updates(cls)
        if cls.sn_reference_properties:
            install_reference_properties(cls, cls.sn_reference_properties)

    def socket_specs(self):
        """(inputs, outputs) the node should have right now. Override when
        sockets depend on properties or other nodes; it's re-checked on
        every update and rebuild."""
        return self.sn_inputs, self.sn_outputs

    def emit(self, ctx):
        """Write this node's code through `ctx` (core/context.NodeContext)."""

    def sn_names(self):
        """Module level names this node defines (classes, operator idnames,
        functions), see core/naming.py. Read them with `ctx.name(key)`."""
        return []

    def sn_name(self, key):
        """A name this node declared in `sn_names()`."""
        from ..core import naming

        return naming.name(self, key)

    # -- life cycle -------------------------------------------------------------

    def init(self, context):
        # the id is set last: property updates during on_create() are ignored
        # until the node is complete (see mark_dirty)
        self.sync_sockets()
        self.on_create()
        self.id = get_short_id()
        self.mark_dirty()

    def on_create(self):
        """Called once after the sockets were created."""

    def copy(self, node):
        self.id = get_short_id()
        self.mark_dirty()

    def free(self):
        errors.clear_node_error(self.id)
        scheduler.request_tree(self.id_data)

    def mark_dirty(self):
        """Something about this node changed: re-check sockets, rebuild soon."""
        if not self.id:
            return  # still being created
        self.sync_sockets()
        scheduler.request_node(self)

    # -- sockets ----------------------------------------------------------------

    def socket(self, key, output=False):
        """Socket by its declared key (identifier), or None."""
        for socket in self.outputs if output else self.inputs:
            if socket.identifier == key:
                return socket
        return None

    def dynamic_sockets(self, key, output=False):
        """Sockets of a dynamic group, without the trailing "+" placeholder."""
        return [
            s
            for s in (self.outputs if output else self.inputs)
            if _in_group(s, key) and not s.is_dynamic
        ]

    def sync_sockets(self):
        """Make the node's sockets match `socket_specs()`, keeping links."""
        key = self.as_pointer()
        # setting a new socket's default fires its update, which would sync
        # this node again in the middle of this sync
        if key in _syncing:
            return False
        _syncing.add(key)
        try:
            inputs, outputs = self.socket_specs()
            changed = _sync(self, self.inputs, inputs, is_output=False)
            changed |= _sync(self, self.outputs, outputs, is_output=True)
            return changed
        finally:
            _syncing.discard(key)

    def add_dynamic_socket(self, identifier, is_output):
        """Turn the "+" socket `identifier` into a normal one, add a new "+"."""
        sockets = self.outputs if is_output else self.inputs
        current = self.socket(identifier, is_output)
        if current is None:
            return
        key = identifier.split("__", 1)[0]
        new = sockets.new(
            current.bl_idname, current.name, identifier=_next_identifier(sockets, key)
        )
        _copy_socket_attrs(current, new)
        new.is_dynamic = True
        pointers = [s.as_pointer() for s in sockets]
        sockets.move(len(sockets) - 1, pointers.index(current.as_pointer()) + 1)
        current.is_dynamic = False
        current.is_removable = True
        self.mark_dirty()

    def update_dynamic_sockets(self):
        """Linking the "+" socket of a group makes it a real one."""
        for is_output, sockets in ((False, self.inputs), (True, self.outputs)):
            for socket in list(sockets):
                if getattr(socket, "is_dynamic", False) and socket.is_linked:
                    self.add_dynamic_socket(socket.identifier, is_output)

    # -- references ---------------------------------------------------------

    @classmethod
    def _ref_collection_attr(cls, prop_name):
        from ..settings.settings import signature_key

        return signature_key(cls.sn_reference_properties[prop_name])

    def resolve_reference(self, prop_name):
        """The node a reference field points to, or None."""
        return find_node(self.get(ref_id_key(prop_name), ""))

    def draw_reference_prop(self, layout, prop_name, text=""):
        layout.prop_search(
            self,
            prop_name,
            bpy.context.scene.sna,
            self._ref_collection_attr(prop_name),
            text=text,
        )

    # -- UI -------------------------------------------------------------------

    def draw_buttons(self, context, layout):
        error = errors.node_message(self.id)
        if error:
            box = layout.box()
            box.alert = True
            box.label(text=error, icon="ERROR")
        if context.scene.sna.dev.show_node_code:
            from ..core.compiler import node_lines

            lines = node_lines.get(self.id)
            if lines:
                col = layout.box().column(align=True)
                for line in lines[:40]:
                    col.label(text=line)
        for prop in self.sn_header_props:
            layout.prop(self, prop, text="")
        self.draw(context, layout)

    def draw(self, context, layout):
        pass


# -----------------------------------------------------------------------------
# Socket syncing
# -----------------------------------------------------------------------------


# pointers of nodes whose sockets are being synced right now
_syncing: set[int] = set()


def _in_group(socket, key):
    return socket.identifier == key or socket.identifier.startswith(key + "__")


def _next_identifier(sockets, key):
    used = {s.identifier for s in sockets}
    i = 1
    while f"{key}__{i}" in used:
        i += 1
    return f"{key}__{i}"


def _copy_socket_attrs(source, target):
    for attr in ("dimension", "use_alpha", "enum_items_data", "kind"):
        if hasattr(source, attr):
            setattr(target, attr, getattr(source, attr))


def _apply_spec(socket, spec: SocketSpec, created):
    name = spec.display_name
    if socket.name != name:
        socket.name = name
    if socket.enabled != spec.enabled:
        socket.enabled = spec.enabled
    if socket.hide != spec.hide:
        socket.hide = spec.hide
    if spec.kind and getattr(socket, "kind", spec.kind) != spec.kind:
        socket.kind = spec.kind
    for attr, value in spec.attrs.items():
        if getattr(socket, attr, value) != value:
            setattr(socket, attr, value)
    if created:
        socket.display_shape = socket.socket_shape
        if socket.is_output and socket.socket_type != "DATA":
            socket.link_limit = 1  # flow code continues in one place
        if spec.default is not MISSING and hasattr(socket, "value"):
            try:
                socket.value = spec.default
            except (TypeError, ValueError):
                pass


def _sync(node, sockets, specs, is_output):
    """Create/remove/reorder `sockets` to match `specs`. Returns True if
    anything structural changed."""
    wanted = []  # (spec, socket or None, identifier)
    for spec in specs:
        if spec.dynamic:
            group = [
                s
                for s in sockets
                if _in_group(s, spec.key) and s.bl_idname == spec.idname
            ]
            if group:
                wanted += [(spec, s, s.identifier) for s in group]
            else:
                wanted.append((spec, None, spec.key))
            continue
        existing = next((s for s in sockets if s.identifier == spec.key), None)
        if existing is not None and existing.bl_idname != spec.idname:
            existing = None
        wanted.append((spec, existing, spec.key))

    keep = {s.as_pointer() for _, s, _ in wanted if s is not None}
    changed = False
    saved_links = {}
    for socket in list(sockets):
        if socket.as_pointer() in keep:
            continue
        # type changed or socket gone: remember its links for a replacement
        others = [l.to_socket if is_output else l.from_socket for l in socket.links]
        if others:
            saved_links[socket.identifier] = others
        sockets.remove(socket)
        changed = True

    tree = node.id_data
    final = []
    for spec, socket, identifier in wanted:
        created = socket is None
        if created:
            socket = sockets.new(spec.idname, spec.display_name, identifier=identifier)
            if spec.dynamic:
                socket.is_dynamic = True
            changed = True
        _apply_spec(socket, spec, created)
        if created:
            for other in saved_links.get(identifier, ()):
                try:
                    if is_output:
                        tree.links.new(socket, other)
                    else:
                        tree.links.new(other, socket)
                except RuntimeError:
                    pass
        final.append(socket)

    for index, socket in enumerate(final):
        pointers = [s.as_pointer() for s in sockets]
        current = pointers.index(socket.as_pointer())
        if current != index:
            sockets.move(current, index)
            changed = True
    return changed
