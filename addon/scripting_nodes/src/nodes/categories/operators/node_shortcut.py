"""Shortcut node: a keymap item in Blender's add-on keyconfig that runs an
operator or opens a menu (helper add_shortcut)."""

import bpy

from ....core import errors, references
from ....core.context import NodeError
from ....lib.sockets import from_socket
from ....core.references import Reference
from ..._operator_call import OperatorCallMixin
from ..._reference_types import OPENABLE_NODES, open_call
from ...base_node import ScriptingBaseNode

# keymaps that hold the shortcuts of an editor or mode (no tools, modal maps)
_SKIPPED = ("Tool:", "Modal", "Gizmo", "Gesture", "Eyedropper", "View2D")
_keymaps = None


def keymaps():
    """{name: space_type} of the keymaps shortcuts can be added to."""
    global _keymaps
    if _keymaps is None:
        from bl_keymap_utils import keymap_hierarchy

        _keymaps = {}

        def walk(items):
            for name, space_type, _region, children in items:
                if not any(word in name for word in _SKIPPED):
                    _keymaps.setdefault(name, space_type)
                walk(children)

        walk(keymap_hierarchy.generate())
    return _keymaps


def _search_keymaps(self, context, edit_text):
    return list(keymaps())


_TYPES = bpy.types.KeyMapItem.bl_rna.properties["type"].enum_items
KEYS = [
    (item.identifier, item.name, "", item.value)
    for item in _TYPES
    if item.identifier != "NONE" and item.name
]
VALUES = [
    ("PRESS", "Press", "When the key is pressed"),
    ("RELEASE", "Release", "When the key is released"),
    ("CLICK", "Click", "Pressed and released without moving the mouse"),
    ("DOUBLE_CLICK", "Double Click", "Pressed twice quickly"),
    ("CLICK_DRAG", "Click Drag", "Pressed and dragged"),
]
MODIFIERS = ("ctrl", "shift", "alt", "oskey")


def key_text(node) -> str:
    """The shortcut as text, "Ctrl Shift A"."""
    names = {"ctrl": "Ctrl", "shift": "Shift", "alt": "Alt", "oskey": "Cmd"}
    parts = [names[m] for m in MODIFIERS if getattr(node, m)]
    key = next((name for ident, name, _, _ in KEYS if ident == node.key), node.key)
    return " ".join(parts + [key])


class SNA_Node_Shortcut(OperatorCallMixin, ScriptingBaseNode, bpy.types.Node):
    """A keyboard shortcut that runs an operator or opens a menu. Users can
    change it in Blender's keymap preferences."""

    bl_idname = "SNA_Node_Shortcut"
    bl_label = "Shortcut"
    sn_root = True

    action: bpy.props.EnumProperty(
        name="Action",
        items=[
            ("OPERATOR", "Run Operator", "Run an operator", "PLAY", 0),
            (
                "MENU",
                "Open Menu",
                "Open a menu, pie menu or panel of this add-on",
                "MENU_PANEL",
                1,
            ),
        ],
    )
    menu: Reference(
        OPENABLE_NODES, name="Menu", description="A Menu, Pie Menu or Panel node"
    )
    key: bpy.props.EnumProperty(name="Key", items=KEYS, default="A")
    ctrl: bpy.props.BoolProperty(name="Ctrl")
    shift: bpy.props.BoolProperty(name="Shift")
    alt: bpy.props.BoolProperty(name="Alt")
    oskey: bpy.props.BoolProperty(name="Cmd", description="Cmd / Windows key")
    value: bpy.props.EnumProperty(name="Event", items=VALUES)
    keymap: bpy.props.StringProperty(
        name="Where",
        description="Where the shortcut works: Window everywhere, an editor or a mode",
        default="Window",
        search=_search_keymaps,
    )

    def socket_specs(self):
        if self.action == "MENU":
            return [], []
        return super().socket_specs()

    def draw(self, context, layout):
        layout.prop(self, "action", text="")
        if self.action == "MENU":
            self.draw_reference(layout, "menu")
        else:
            self.draw_operator_picker(layout)
        row = layout.row(align=True)
        op = row.operator(
            "sna.record_shortcut", text=key_text(self), icon="EVENT_RETURN"
        )
        op.node_id = self.id
        row.prop(self, "key", text="", icon_only=True)
        row = layout.row(align=True)
        for modifier in MODIFIERS:
            row.prop(self, modifier, toggle=True)
        sub = layout.row()
        sub.alert = self.keymap not in keymaps()
        sub.prop(self, "keymap", text="", icon="KEYINGSET")
        layout.prop(self, "value", text="")

    def setup_hint(self):
        if self.action == "MENU":
            if not references.target_id(self, "menu"):
                return "Pick a menu"
            return ScriptingBaseNode.setup_hint(self)
        return self.unset_hint() or super().setup_hint()

    def unset_hint(self):
        """Inputs linked to a node with an error: left out of the shortcut
        (their value is fixed when the add-on registers, e.g. Event Info has
        no event then)."""
        names = []
        for socket in self.inputs:
            source = from_socket(socket) if socket.is_linked else None
            node = source.node if source is not None else None
            if node is not None and errors.node_message(getattr(node, "id", "")):
                names.append(f"{socket.name} ({node.label or node.bl_label})")
        if not names:
            return None
        return (
            f"Gets no value, the operator's default is used: {', '.join(names)}. "
            "Shortcut values are set when the add-on is enabled"
        )

    def emit(self, ctx):
        space_type = keymaps().get(self.keymap)
        if space_type is None:
            raise NodeError(f"Unknown place '{self.keymap}', pick one from the list")
        properties = {}
        if self.action == "MENU":
            target = self.resolve_reference("menu")
            if target is None:
                raise NodeError("Pick a menu")
            idname, call = open_call(target)
            properties.update(call)
        else:
            idname = self.operator_idname()
            if not idname:
                raise NodeError("Pick an operator")
            # a value that's None (the node giving it failed) is left out:
            # keymap items can't hold None, register() would fail
            args = self.operator_args(ctx)
            properties.update((name, value) for name, value in args if value != "None")
        args = [repr(self.keymap), repr(space_type), repr(idname), repr(self.key)]
        if self.value != "PRESS":
            args.append(repr(self.value))
        if properties:
            items = ", ".join(
                f"{name!r}: {value}" for name, value in properties.items()
            )
            args.append(f"properties={{{items}}}")
        args += [f"{m}=True" for m in MODIFIERS if getattr(self, m)]
        ctx.on_register(f"{ctx.helper('add_shortcut')}({', '.join(args)})")
