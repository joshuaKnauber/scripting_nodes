from textwrap import wrap
from typing import Dict, Literal, Set, Tuple

import bpy

from ..core import errors, scheduler
from ..core.references import (
    find_node,
    install_reference_properties,
    ref_id_key,
)
from ..lib.ids import get_short_id
from ..lib.sockets import from_nodes, socket_index, to_nodes
from ..node_tree.node_tree import ScriptingNodeTree
from ..sockets.socket_types import SOCKET_IDNAME_TYPE

CODE_FIELDS = (
    "code_imports",
    "code_module",
    "code_inline",
    "code_global",
    "code_register",
    "code_unregister",
)


class ScriptingBaseNode:
    """Base class of every Scripting Nodes node.

    Subclasses implement `on_create()` (add sockets) and `generate()` (fill
    the code fields below and `output.code` of data outputs). Anything that
    changes the generated code calls `self._generate()`, which only *requests*
    regeneration - the scheduler runs `generate()` on its next flush.

    Code fields:
      code_imports     import lines, deduplicated per module
      code_global      module-level code
      code_module      module-level code of ROOT_NODE nodes (classes, ...)
      code_inline      statement(s) inside a program flow
      code_register    lines for the module's register()
      code_unregister  lines for the module's unregister()
    """

    @classmethod
    def poll(cls, ntree):
        """Checks if the node is valid"""
        return ntree.bl_idname == ScriptingNodeTree.bl_idname

    def ntree_poll(self, group):
        """Checks if the node tree is valid"""
        return group.bl_idname == ScriptingNodeTree.bl_idname

    @property
    def node_tree(self):
        """Returns the node tree this node lives in (overridden by Group)."""
        return self.id_data

    ### Properties

    is_sn = True

    sn_options: Set[Literal["ROOT_NODE"]] = set()
    # {prop_name: tuple-of-allowed-bl_idnames}. Each entry declares a string
    # field referencing another node. The field is stored by node id (see
    # core/references.py); the tuple filters which nodes the picker shows.
    sn_reference_properties: Dict[str, Tuple[str, ...]] = {}
    # PointerProperty fields whose value is another ScriptingNodeTree.
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

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.sn_reference_properties:
            install_reference_properties(cls, cls.sn_reference_properties)

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
        errors.clear_node_error(self.id)
        scheduler.request_tree(self.id_data)

    ### Code Generation

    def _generate(self):
        """Request regeneration of this node (runs on the next flush)."""
        scheduler.request_node(self)

    def generate(self):
        raise NotImplementedError

    def _code_snapshot(self):
        """(statement/module code, data output code, layout names)"""
        return (
            tuple(getattr(self, field) for field in CODE_FIELDS),
            tuple(getattr(s, "code", "") for s in self.outputs),
            tuple(getattr(s, "layout", "") for s in self.outputs),
        )

    def regenerate(self) -> tuple[bool, bool, bool]:
        """Run generate() now. Only the scheduler calls this.

        Returns which parts changed: (code, data outputs, layouts). Errors in
        generate() are stored per node and shown on it; the node then
        contributes no code.
        """
        unchanged = (False, False, False)
        if not self.id:
            return unchanged
        # Mid-edit states (e.g. a reroute being inserted) can leave non-SN
        # sockets on the node; keep the previous code until it settles.
        for socket in list(self.inputs) + list(self.outputs):
            if not hasattr(socket, "eval"):
                return unchanged
        before = self._code_snapshot()
        self._clear_code()
        try:
            self.generate()
            errors.clear_node_error(self.id)
        except Exception as exc:
            errors.set_node_error(self.id, exc)
            self._clear_code()
        after = self._code_snapshot()
        return tuple(a != b for a, b in zip(before, after))

    def _clear_code(self):
        for field in CODE_FIELDS:
            setattr(self, field, "")
        for out in self.outputs:
            out.code = ""

    def dependent_nodes(self, changes):
        """Nodes whose generated code reads the parts of this node that changed.

        - code: upstream nodes embed our `code_inline` (via program inputs)
        - data outputs: downstream nodes read `output.code`
        - layouts: downstream program/interface nodes read the layout name
        """
        code, outputs, layouts = changes
        for out in self.outputs:
            if getattr(out, "socket_type", None) == "DATA":
                if outputs:
                    yield from to_nodes(out)
            elif layouts:
                yield from to_nodes(out)
        if code:
            for inp in self.inputs:
                if getattr(inp, "socket_type", None) == "PROGRAM":
                    yield from from_nodes(inp)

    def code_dependencies(self):
        """Nodes whose code should be generated before this one."""
        for inp in self.inputs:
            if getattr(inp, "socket_type", None) == "DATA":
                yield from from_nodes(inp)
        for out in self.outputs:
            if getattr(out, "socket_type", None) == "PROGRAM":
                yield from to_nodes(out)

    def on_ref_change(self, node):
        """A node this node references changed its code."""
        self._generate()

    ### Reference helpers

    @classmethod
    def _ref_collection_attr(cls, prop_name):
        """scene.sna attribute name of the picker collection for this field."""
        from ..settings.settings import signature_key

        return signature_key(cls.sn_reference_properties[prop_name])

    def resolve_reference(self, prop_name):
        """Return the node a reference-property points to, or None."""
        return find_node(self.get(ref_id_key(prop_name), ""))

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
        return target is not None and target.id_data is not self.id_data

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

    def update_dynamic_sockets(self):
        """A linked dynamic socket becomes a normal (removable) one and a new
        empty dynamic socket is added after it."""
        for sockets, add in (
            (self.inputs, self.add_input),
            (self.outputs, self.add_output),
        ):
            for socket in list(sockets):
                if getattr(socket, "is_dynamic", False) and socket.is_linked:
                    index = socket_index(self, socket)
                    add(socket.bl_idname, socket.label, dynamic=True)
                    sockets.move(len(sockets) - 1, index + 1)
                    socket.is_dynamic = False
                    socket.is_removable = True

    ### UI

    def _shown_code_lines(self):
        """Compact code lines for the in-node dev preview."""
        shown = self.code_module or self.code_inline
        if not shown:
            return []

        lines = [line.rstrip() for line in shown.strip().splitlines()]
        lines = [line for line in lines if line.strip()]

        display_lines = []
        for line in lines:
            indent = line[: len(line) - len(line.lstrip())]
            chunks = wrap(
                line,
                width=96,
                subsequent_indent=f"{indent}    ",
                replace_whitespace=False,
                drop_whitespace=False,
            )
            display_lines.extend(chunks or [line])
        return display_lines

    def draw_buttons(self, context, layout):
        error = errors.node_errors.get(self.id)
        if error:
            box = layout.box()
            box.alert = True
            box.label(text=error, icon="ERROR")
        if bpy.context.scene.sna.dev.show_node_code:
            box = layout.box()
            col = box.column(align=True)
            for line in self._shown_code_lines():
                col.label(text=line)
        self.draw(context, layout)

    def draw(self, context, layout):
        pass
