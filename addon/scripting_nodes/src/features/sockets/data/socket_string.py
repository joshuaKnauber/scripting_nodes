from ..base_socket import ScriptingBaseSocket
import bpy


# Item-list encoding: records separated by \x1e, fields by \x1f.
# Field 0 = identifier, field 1 = label (falls back to identifier).
_ITEM_SEP = "\x1e"
_FIELD_SEP = "\x1f"


def encode_enum_items(items):
    """Pack a list of (identifier, label) pairs into the storage string.

    Empty list / falsy input encodes as "" - which the socket treats as
    plain-string mode.
    """
    parts = []
    for entry in items or ():
        if isinstance(entry, str):
            ident, label = entry, entry
        else:
            ident = entry[0]
            label = entry[1] if len(entry) > 1 else entry[0]
        parts.append(f"{ident}{_FIELD_SEP}{label}")
    return _ITEM_SEP.join(parts)


# Items returned from the EnumProperty callback must stay alive across draws
# (Blender holds raw string pointers into the returned list). Cache keyed by
# the encoded data string so identical item-lists share one cache entry.
_ITEMS_CACHE: dict = {}


def _enum_items_callback(self, context):
    data = self.enum_items_data
    cached = _ITEMS_CACHE.get(data)
    if cached is None:
        cached = []
        for entry in data.split(_ITEM_SEP):
            if not entry:
                continue
            parts = entry.split(_FIELD_SEP)
            ident = parts[0]
            label = parts[1] if len(parts) > 1 else ident
            cached.append((ident, label, ""))
        # An empty dropdown crashes Blender's enum widget; seed a sentinel.
        if not cached:
            cached = [("", "", "")]
        _ITEMS_CACHE[data] = cached
    return cached


def enum_value_get(self):
    items = _enum_items_callback(self, bpy.context)
    current = self.value
    for i, item in enumerate(items):
        if item[0] == current:
            return i
    return 0


def enum_value_set(self, idx):
    items = _enum_items_callback(self, bpy.context)
    if 0 <= idx < len(items):
        # Writing `value` triggers its own update_value -> _generate().
        self.value = items[idx][0]


class ScriptingStringSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingStringSocket"
    bl_label = "String"

    def update_value(self, context):
        self.node._generate()

    value: bpy.props.StringProperty(
        default="", update=update_value, options={"TEXTEDIT_UPDATE"}
    )

    # Non-empty enables enum-dropdown mode. Encode/decode with the
    # encode_enum_items helper.
    enum_items_data: bpy.props.StringProperty(default="")

    # UI projection of `value` as a dropdown. Items are derived per-socket
    # from `enum_items_data`; the get/set callbacks keep `value` as the
    # canonical store so code emission is unchanged.
    enum_value: bpy.props.EnumProperty(
        items=_enum_items_callback,
        get=enum_value_get,
        set=enum_value_set,
    )

    def _to_code(self):
        return f'"{self.value}"'

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        elif self.enum_items_data:
            layout.prop(self, "enum_value", text=self.name)
        else:
            layout.prop(self, "value", text=self.name)

    @classmethod
    def draw_color_simple(cls):
        return (0.4, 0.6, 1, 1)
