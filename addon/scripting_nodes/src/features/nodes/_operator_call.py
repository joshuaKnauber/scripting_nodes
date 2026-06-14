"""Shared machinery for nodes that invoke an operator (Run Operator + Button).

Both nodes need the same three things:

  1. A picker that toggles between an SN operator (referenced by node) and a
     built-in Blender operator (picked from a searchable enum).
  2. Dynamic input sockets that mirror the chosen operator's properties.
     Each socket name = property name; type chosen from the prop's Blender
     type. Reconciliation preserves links across operator changes when the
     same-named socket survives.
  3. Code emission for the kwargs, so each node's `generate()` just splices
     the args string into its own call template.

The `OperatorCallMixin` provides all of that. Concrete nodes declare
`operator_arg_offset` so the mixin knows where its dynamic sockets start.
"""

from typing import List, Optional, Tuple
from ._reference_signatures import VARIABLE_NODES  # noqa: F401 (kept for parity)
from ..sockets.data.socket_string import encode_enum_items
import bpy


# Tuple used by Run Operator and Button to filter the SN operator picker.
OPERATOR_NODES = ("SNA_Node_Operator",)


# -----------------------------------------------------------------------------
# Property-type → socket mapping
# -----------------------------------------------------------------------------


def _prop_spec(prop) -> Optional[Tuple[str, str, object, int, str]]:
    """Map a Blender RNA property to (socket_idname, default, vector_dim, enum_data).

    `enum_data` is the encoded items string for enum props (consumed by the
    StringSocket's enum-dropdown mode), or "" for other types.

    Returns None for prop types we don't support (Pointer, Collection,
    size>4 vectors). Caller should skip those.
    """
    # Skip operator-internal props that aren't meant to be set from outside.
    if "HIDDEN" in getattr(prop, "options", set()):
        return None

    ptype = prop.type
    if ptype == "BOOLEAN":
        if prop.is_array:
            return None  # bool arrays are rare on operators, punt
        return ("ScriptingBooleanSocket", bool(prop.default), 0, "")
    if ptype == "INT":
        if prop.is_array:
            return None
        return ("ScriptingIntegerSocket", int(prop.default), 0, "")
    if ptype == "FLOAT":
        if prop.is_array:
            size = prop.array_length
            if size < 2 or size > 4:
                return None
            subtype = getattr(prop, "subtype", "NONE")
            default = tuple(prop.default_array)
            if subtype in {"COLOR", "COLOR_GAMMA"}:
                return ("ScriptingColorSocket", default, size, "")
            return ("ScriptingVectorSocket", default, size, "")
        return ("ScriptingFloatSocket", float(prop.default), 0, "")
    if ptype == "STRING":
        return ("ScriptingStringSocket", str(prop.default), 0, "")
    if ptype == "ENUM":
        # String socket in enum-dropdown mode: identifier stored in `value`,
        # items list serialized into `enum_items_data` so the socket renders
        # a dropdown instead of a free text field.
        items = [(item.identifier, item.name or item.identifier) for item in prop.enum_items]
        return ("ScriptingStringSocket", str(prop.default), 0, encode_enum_items(items))
    # POINTER / COLLECTION fall through.
    return None


def _apply_default(socket, idname: str, default, vector_dim: int, enum_data: str = "") -> None:
    """Set the socket's `value` to the operator-provided default. For enum
    props on a StringSocket, also seed `enum_items_data` so the socket
    renders as a dropdown."""
    if not hasattr(socket, "value"):
        return
    try:
        if idname == "ScriptingVectorSocket":
            # The vector socket stores a size-4 array; we tell it which
            # dimension to actually emit.
            socket.dimension = str(vector_dim)
            padded = tuple(default) + (0.0,) * (4 - len(default))
            socket.value = padded
        elif idname == "ScriptingColorSocket":
            socket.use_alpha = vector_dim == 4
            padded = tuple(default) + (1.0,) * (4 - len(default))
            socket.value = padded
        elif idname == "ScriptingStringSocket":
            # Set items_data first so the dropdown is wired before value lands.
            socket.enum_items_data = enum_data
            socket.value = default
        else:
            socket.value = default
    except (TypeError, ValueError):
        # Defaults can occasionally be out of range for the socket; ignoring
        # leaves the socket at its own default, which is safe.
        pass


# -----------------------------------------------------------------------------
# Blender operator collection (session-local, backs the picker's prop_search)
# -----------------------------------------------------------------------------


class SNA_BlenderOperatorRef(bpy.types.PropertyGroup):
    """One entry per Blender operator. Mirrors the SNA_NodeReference shape:
    `name` is searched/stored by prop_search, `bl_idname` is the canonical
    dotted id used in generated code."""

    # Format: "Add Cube  [mesh.primitive_cube_add]" so fuzzy search matches
    # either the human label or the bl_idname.
    name: bpy.props.StringProperty()
    bl_idname: bpy.props.StringProperty()


def _populate_blender_operator_collection(coll) -> None:
    coll.clear()
    entries = []
    for cat_name in dir(bpy.ops):
        if cat_name.startswith("_"):
            continue
        cat = getattr(bpy.ops, cat_name)
        for op_name in dir(cat):
            if op_name.startswith("_"):
                continue
            try:
                op = getattr(cat, op_name)
                rna = op.get_rna_type()
            except (AttributeError, RuntimeError):
                continue
            bl_idname = f"{cat_name}.{op_name}"
            label = rna.name or bl_idname
            entries.append((f"{label}  [{bl_idname}]", bl_idname))
    entries.sort(key=lambda e: e[0].lower())
    for display, bl_idname in entries:
        entry = coll.add()
        entry.name = display
        entry.bl_idname = bl_idname


def refresh_blender_operator_collection() -> None:
    wm = bpy.context.window_manager
    if hasattr(wm, "sna_blender_operators"):
        _populate_blender_operator_collection(wm.sna_blender_operators)


def _resolve_blender_op_name(picker_value: str) -> str:
    """Map the picker's stored display string back to a dotted bl_idname."""
    if not picker_value:
        return ""
    wm = bpy.context.window_manager
    coll = getattr(wm, "sna_blender_operators", None)
    if coll is None:
        return ""
    entry = coll.get(picker_value)
    return entry.bl_idname if entry else ""


# -----------------------------------------------------------------------------
# Operator-prop introspection (SN + Blender, unified result format)
# -----------------------------------------------------------------------------


def _sn_operator_prop_specs(op_node) -> List[Tuple[str, str, object, int, str]]:
    """Specs derived from an SN Operator node's attached class-body properties.

    Each attached entry whose register_on=="Operator" contributes one socket.
    SN enum-property items can be sourced dynamically (List input / Variable),
    so we don't try to introspect them - the socket stays a plain string.
    """
    specs = []
    if op_node is None:
        return specs
    for _entry, prop_node in op_node.iter_attached_property_nodes():
        if getattr(prop_node, "register_on", "") != "Operator":
            continue
        name = getattr(prop_node, "prop_name", "")
        if not name:
            continue
        idname = _socket_for_sn_property(prop_node)
        if idname is None:
            continue
        default = _default_for_sn_property(prop_node, idname)
        vector_dim = 3 if idname in {"ScriptingVectorSocket", "ScriptingColorSocket"} else 0
        specs.append((name, idname, default, vector_dim, ""))
    return specs


_SN_PROP_TO_SOCKET = {
    "SNA_Node_BoolProperty": "ScriptingBooleanSocket",
    "SNA_Node_IntProperty": "ScriptingIntegerSocket",
    "SNA_Node_FloatProperty": "ScriptingFloatSocket",
    "SNA_Node_StringProperty": "ScriptingStringSocket",
    "SNA_Node_FloatVectorProperty": "ScriptingVectorSocket",
    "SNA_Node_EnumProperty": "ScriptingStringSocket",
}


def _socket_for_sn_property(prop_node) -> Optional[str]:
    return _SN_PROP_TO_SOCKET.get(prop_node.bl_idname)


def _default_for_sn_property(prop_node, idname: str):
    """Best-effort default — falls back to the socket's own default."""
    val = getattr(prop_node, "prop_default", None)
    if val is None:
        if idname == "ScriptingBooleanSocket":
            return False
        if idname == "ScriptingIntegerSocket":
            return 0
        if idname == "ScriptingFloatSocket":
            return 0.0
        if idname == "ScriptingStringSocket":
            return ""
        if idname == "ScriptingVectorSocket":
            return (0.0, 0.0, 0.0)
    return val


def _blender_operator_prop_specs(
    bl_idname: str,
) -> List[Tuple[str, str, object, int, str]]:
    """Specs derived from a Blender operator's RNA properties."""
    if not bl_idname or "." not in bl_idname:
        return []
    cat_name, op_name = bl_idname.split(".", 1)
    try:
        op = getattr(getattr(bpy.ops, cat_name), op_name)
        rna = op.get_rna_type()
    except (AttributeError, RuntimeError):
        return []

    specs = []
    for prop in rna.properties:
        if prop.identifier == "rna_type":
            continue
        spec = _prop_spec(prop)
        if spec is None:
            continue
        idname, default, vector_dim, enum_data = spec
        specs.append((prop.identifier, idname, default, vector_dim, enum_data))
    return specs


def register():
    bpy.types.WindowManager.sna_blender_operators = bpy.props.CollectionProperty(
        type=SNA_BlenderOperatorRef
    )


def unregister():
    try:
        del bpy.types.WindowManager.sna_blender_operators
    except AttributeError:
        pass


# -----------------------------------------------------------------------------
# Mixin
# -----------------------------------------------------------------------------


# Execution-context flags accepted by bpy.ops calls. Useful for Run Operator
# only; Button takes its context from the UI.
EXEC_CONTEXT_ITEMS = [
    ("EXEC_DEFAULT", "Exec Default", "Run execute() directly"),
    ("INVOKE_DEFAULT", "Invoke Default", "Run invoke() then execute() (uses UI context)"),
    ("EXEC_REGION_WIN", "Exec Region Win", "Run execute() in window region context"),
    ("INVOKE_REGION_WIN", "Invoke Region Win", "Run invoke() in window region context"),
    ("EXEC_AREA", "Exec Area", "Run execute() in area context"),
    ("INVOKE_AREA", "Invoke Area", "Run invoke() in area context"),
    ("EXEC_SCREEN", "Exec Screen", "Run execute() in screen context"),
    ("INVOKE_SCREEN", "Invoke Screen", "Run invoke() in screen context"),
]


class OperatorCallMixin:
    """Shared picker + socket reconciler + kwargs emitter.

    Subclasses must define:
      - `operator_arg_offset`: the count of fixed input sockets that appear
        before the dynamic per-arg sockets.

    Subclasses should call `reconcile_operator_sockets()` in their update
    callbacks and `iter_operator_arg_sockets()` from `generate()`.
    """

    sn_reference_properties = {"operator_sn": OPERATOR_NODES}

    operator_arg_offset: int = 0

    # ---- mode + target -----------------------------------------------------

    def update_operator_target(self, context):
        self.reconcile_operator_sockets()
        self._generate()

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("CUSTOM", "Custom", "Reference an Operator node in this addon"),
            ("BLENDER", "Blender", "Call a built-in Blender operator"),
        ],
        default="CUSTOM",
        update=update_operator_target,
    )

    operator_sn: bpy.props.StringProperty(
        name="Operator",
        description="An Operator node in this addon",
        update=update_operator_target,
    )

    operator_blender: bpy.props.StringProperty(
        name="Blender Operator",
        description="A built-in Blender operator",
        update=update_operator_target,
    )

    # ---- introspection -----------------------------------------------------

    def _resolved_bl_idname(self) -> str:
        """The dotted bl_idname of the currently chosen operator, or ""."""
        if self.mode == "CUSTOM":
            target = self.resolve_reference("operator_sn")
            if target is None:
                return ""
            namespace = bpy.context.scene.sna.addon.idname_namespace
            return f"{namespace}.operator_{target.id.lower()}"
        return _resolve_blender_op_name(self.operator_blender)

    def _target_prop_specs(self) -> List[Tuple[str, str, object, int, str]]:
        if self.mode == "CUSTOM":
            return _sn_operator_prop_specs(self.resolve_reference("operator_sn"))
        return _blender_operator_prop_specs(self._resolved_bl_idname())

    # ---- socket reconciliation --------------------------------------------

    def reconcile_operator_sockets(self) -> None:
        """Sync the dynamic op-arg input sockets with the chosen operator.

        Sockets after `operator_arg_offset` are treated as op-args. Existing
        sockets that match a target prop by name AND idname are preserved
        (with their links). Others are removed; missing ones are added.
        """
        target = self._target_prop_specs()
        offset = self.operator_arg_offset
        target_by_name = {spec[0]: spec for spec in target}

        # Phase 1: prune sockets that don't survive.
        i = offset
        while i < len(self.inputs):
            socket = self.inputs[i]
            keep_spec = target_by_name.get(socket.name)
            if keep_spec is None or keep_spec[1] != socket.bl_idname:
                self.inputs.remove(socket)
                continue
            i += 1

        # Phase 2: add missing ones in target order, then enforce order.
        # Survivors also get enum_items_data refreshed - if the chosen
        # operator changed but a same-typed socket survived (e.g. another
        # operator with an `align` enum), the dropdown options need to
        # match the new operator's items.
        for target_idx, (name, idname, default, vector_dim, enum_data) in enumerate(target):
            existing = self.inputs.get(name)
            desired_idx = offset + target_idx
            if existing is None:
                socket = self.add_input(idname, name)
                _apply_default(socket, idname, default, vector_dim, enum_data)
                self.inputs.move(len(self.inputs) - 1, desired_idx)
            else:
                if idname == "ScriptingStringSocket" and existing.enum_items_data != enum_data:
                    existing.enum_items_data = enum_data
                current_idx = list(self.inputs).index(existing)
                if current_idx != desired_idx:
                    self.inputs.move(current_idx, desired_idx)

    def iter_operator_arg_sockets(self):
        """Yield the dynamic op-arg sockets in declaration order."""
        for socket in list(self.inputs)[self.operator_arg_offset:]:
            yield socket

    def on_ref_change(self, node):
        # SN operator's class body changed - re-derive sockets.
        self.reconcile_operator_sockets()
        self._generate()

    # ---- code emission helpers --------------------------------------------

    def emit_kwargs_inline(self) -> str:
        """Format `k1=v1, k2=v2, ...` for bpy.ops style calls."""
        parts = []
        for socket in self.iter_operator_arg_sockets():
            parts.append(f"{socket.name}={socket.eval()}")
        return ", ".join(parts)

    def emit_op_property_lines(self, op_var: str) -> str:
        """Format `op_var.k1 = v1\\nop_var.k2 = v2\\n...` for layout.operator style."""
        lines = []
        for socket in self.iter_operator_arg_sockets():
            lines.append(f"{op_var}.{socket.name} = {socket.eval()}")
        return "\n".join(lines)

    # ---- shared picker UI -------------------------------------------------

    def draw_operator_picker(self, layout) -> None:
        row = layout.row(align=True)
        if self.mode == "CUSTOM":
            self.draw_reference_prop(row, "operator_sn")
            row.prop(self, "mode", icon="USER", icon_only=True, text="")
        else:
            wm = bpy.context.window_manager
            coll = getattr(wm, "sna_blender_operators", None)
            # Lazy populate on first draw - register-time timing is fragile
            # across hot-reload and session restore.
            if coll is not None and len(coll) == 0:
                _populate_blender_operator_collection(coll)
            row.prop_search(
                self,
                "operator_blender",
                wm,
                "sna_blender_operators",
                text="",
            )
            row.prop(self, "mode", icon="BLENDER", icon_only=True, text="")
