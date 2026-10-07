"""Shared machinery for nodes that invoke an operator (Run Operator + Button).

Both nodes need the same three things:

  1. A picker that toggles between an SN operator (referenced by node) and a
     built-in Blender operator (picked from a searchable enum).
  2. Dynamic input sockets that mirror the chosen operator's properties.
     Each socket name = property name; type chosen from the prop's Blender
     type. Reconciliation preserves links across operator changes when the
     same-named socket survives.
  3. The arguments as (name, expression) pairs for the node's own template.

The `OperatorCallMixin` provides all of that. Concrete nodes declare
`fixed_inputs`; one socket per operator property follows them.
"""

import math
from typing import List, Optional, Tuple

import bpy

from ..core import naming
from ..sockets.data.socket_string import encode_enum_items
from ..sockets.spec import Socket


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
        if prop.is_enum_flag:
            return None  # takes a set of items, a single string won't do
        # String socket in enum-dropdown mode: identifier stored in `value`,
        # items list serialized into `enum_items_data` so the socket renders
        # a dropdown instead of a free text field.
        items = [
            (item.identifier, item.name or item.identifier) for item in prop.enum_items
        ]
        return ("ScriptingStringSocket", str(prop.default), 0, encode_enum_items(items))
    # POINTER / COLLECTION fall through.
    return None


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
    """Specs from the properties attached to an SN Operator node."""
    specs = []
    if op_node is None:
        return specs
    for prop_node in op_node.attached_properties():
        idname = getattr(prop_node, "data_type", "ScriptingDataSocket")
        default = getattr(prop_node, "prop_default", None)
        dim = 3 if idname in {"ScriptingVectorSocket", "ScriptingColorSocket"} else 0
        specs.append((prop_node.prop_name, idname, default, dim, ""))
    return specs


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


def _equals_default(socket, default) -> bool:
    """True if the socket's own value is the operator property's default."""
    value = getattr(socket, "value", None)
    if value is None or default is None:
        return False
    if isinstance(default, (tuple, list)):
        values = tuple(value)[: len(default)]
        return len(values) == len(default) and all(
            math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-6)
            for a, b in zip(values, default)
        )
    if isinstance(default, float):
        return math.isclose(value, default, rel_tol=1e-6, abs_tol=1e-6)
    return value == default


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
    (
        "INVOKE_DEFAULT",
        "Invoke Default",
        "Run invoke() then execute() (uses UI context)",
    ),
    ("EXEC_REGION_WIN", "Exec Region Win", "Run execute() in window region context"),
    ("INVOKE_REGION_WIN", "Invoke Region Win", "Run invoke() in window region context"),
    ("EXEC_AREA", "Exec Area", "Run execute() in area context"),
    ("INVOKE_AREA", "Invoke Area", "Run invoke() in area context"),
    ("EXEC_SCREEN", "Exec Screen", "Run execute() in screen context"),
    ("INVOKE_SCREEN", "Invoke Screen", "Run invoke() in screen context"),
]

ARG_PREFIX = "arg_"

# pointers of nodes whose sockets are being synced right now
_syncing: set = set()


class OperatorCallMixin:
    """Operator picker + one input socket per operator property.

    Subclasses define `fixed_inputs` / `fixed_outputs` (socket specs) and use
    `operator_idname()` and `operator_args(ctx)` in emit()."""

    sn_reference_properties = {"operator_sn": OPERATOR_NODES}
    fixed_inputs: list = []
    fixed_outputs: list = []

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("CUSTOM", "Custom", "Reference an Operator node in this addon"),
            ("BLENDER", "Blender", "Call a built-in Blender operator"),
        ],
        default="CUSTOM",
    )
    operator_sn: bpy.props.StringProperty(
        name="Operator", description="An Operator node"
    )
    operator_blender: bpy.props.StringProperty(
        name="Blender Operator", description="A built-in Blender operator"
    )

    def operator_idname(self) -> str:
        """Dotted bl_idname of the chosen operator, or ""."""
        if self.mode == "CUSTOM":
            target = self.resolve_reference("operator_sn")
            return naming.idname(target, "operator") if target else ""
        return _resolve_blender_op_name(self.operator_blender)

    def _target_prop_specs(self):
        if self.mode == "CUSTOM":
            return _sn_operator_prop_specs(self.resolve_reference("operator_sn"))
        return _blender_operator_prop_specs(self.operator_idname())

    def sync_sockets(self):
        # Sockets created after the node exists get their default value set,
        # whose update callback would sync this node again in the middle of
        # this sync (base_node._apply_spec -> update_value -> mark_dirty).
        key = self.as_pointer()
        if key in _syncing:
            return False
        _syncing.add(key)
        try:
            return super().sync_sockets()
        finally:
            _syncing.discard(key)

    def socket_specs(self):
        inputs = list(self.fixed_inputs)
        for name, idname, default, vector_dim, enum_data in self._target_prop_specs():
            spec = Socket(idname, ARG_PREFIX + name, name)
            if default is not None:
                if idname in {"ScriptingVectorSocket", "ScriptingColorSocket"}:
                    filler = 1.0 if idname == "ScriptingColorSocket" else 0.0
                    default = tuple(default) + (filler,) * (4 - len(default))
                spec.default = default
            if idname == "ScriptingVectorSocket" and vector_dim:
                spec.attrs["dimension"] = str(vector_dim)
            if idname == "ScriptingColorSocket":
                spec.attrs["use_alpha"] = vector_dim == 4
            if enum_data:
                spec.attrs["enum_items_data"] = enum_data
            inputs.append(spec)
        return inputs, list(self.fixed_outputs)

    def operator_args(self, ctx) -> list[tuple[str, str]]:
        """(property name, expression) for every operator property socket.

        Blender operators often behave differently when a property isn't set
        (e.g. Add Cube places the cube at the 3D cursor unless `location` is
        given), so unconnected sockets still at the operator's default are
        left out for them."""
        defaults = {}
        if self.mode == "BLENDER":
            defaults = {spec[0]: spec[2] for spec in self._target_prop_specs()}
        args = []
        for socket in self.inputs:
            if not socket.identifier.startswith(ARG_PREFIX):
                continue
            name = socket.identifier[len(ARG_PREFIX) :]
            if (
                not socket.is_linked
                and name in defaults
                and _equals_default(socket, defaults[name])
            ):
                continue
            args.append((name, ctx.input(socket.identifier)))
        return args

    def draw_operator_picker(self, layout) -> None:
        row = layout.row(align=True)
        if self.mode == "CUSTOM":
            self.draw_reference_prop(row, "operator_sn")
            row.prop(self, "mode", icon="USER", icon_only=True, text="")
        else:
            wm = bpy.context.window_manager
            coll = getattr(wm, "sna_blender_operators", None)
            # filled on first draw: register-time timing is fragile
            if coll is not None and len(coll) == 0:
                _populate_blender_operator_collection(coll)
            row.prop_search(
                self, "operator_blender", wm, "sna_blender_operators", text=""
            )
            row.prop(self, "mode", icon="BLENDER", icon_only=True, text="")
