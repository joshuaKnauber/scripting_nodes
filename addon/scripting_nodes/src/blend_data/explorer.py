"""The data explorer: Blender's data of the open file, one level at a time
(blend_data/ui/explorer_panel.py).

A Location is a path with concrete keys, like a Blender Data node's path:

    Location("CONTEXT", ["active_object", "modifiers", "[]"], [Key("NAME", "Bevel")])

It either follows the active Blender Data node (`node_location`, moving it
changes the node's path) or is the explorer's own place, stored as a Python
path in `scene.sna.ui.explorer_path` (`free_location`).

`evaluate()` walks the path through the live data. Where that isn't possible
(nothing active, a key from a link) the explorer falls back to the types
(rna.py), without values.
"""

from dataclasses import dataclass, field

import bpy

from . import rna


@dataclass(frozen=True)
class Key:
    """How a `[]` picks its item. `value` is None if it isn't known (the
    node's key input is linked)."""

    mode: str  # INDEX, NAME or ACTIVE
    value: object = None

    def label(self) -> str:
        if self.mode == "ACTIVE":
            return "Active"
        if self.value is None:
            return "…"
        return str(self.value) if self.mode == "NAME" else f"[{self.value}]"


@dataclass
class Location:
    root: str  # CONTEXT, DATA or INPUT; "" for the list of roots
    parts: list = field(default_factory=list)
    keys: list = field(default_factory=list)  # one Key per "[]"
    input_type: str = ""  # INPUT: type of the data the path starts at
    # INPUT: live data the path starts at, or None if it isn't known
    start: object = None

    def root_step(self):
        if self.root == "INPUT":
            return rna.root_step(self.input_type)
        return rna.root_step(rna.ROOT_TYPES[self.root])

    def steps(self):
        return rna.resolve(self.root_step(), self.parts)

    def final_step(self):
        steps = self.steps()
        return steps[-1] if steps else self.root_step()

    def extended(self, name=None, key=None) -> "Location":
        """This location plus attribute `name`, or plus an item (`key`)."""
        if key is not None:
            return Location(
                self.root, self.parts + [rna.SUBSCRIPT], self.keys + [key],
                self.input_type, self.start,
            )  # fmt: skip
        return Location(
            self.root, self.parts + [name], list(self.keys), self.input_type, self.start
        )

    def truncated(self, count) -> "Location":
        """The first `count` segments of this location."""
        parts = self.parts[:count]
        keys = self.keys[: parts.count(rna.SUBSCRIPT)]
        return Location(self.root, parts, keys, self.input_type, self.start)

    def python(self) -> str:
        """`bpy.context.active_object.modifiers["Bevel"]` (free locations)."""
        text = {"CONTEXT": "bpy.context", "DATA": "bpy.data"}.get(self.root, "")
        keys = iter(self.keys)
        for part in self.parts:
            if part != rna.SUBSCRIPT:
                text += f".{part}"
                continue
            key = next(keys)
            if key.mode == "ACTIVE":
                text += ".active"
            else:
                text += f"[{key.value!r}]"
        return text

    def crumbs(self):
        """(label, segment count) of every step, the root first."""
        if self.root == "INPUT":
            first = rna.display_name(self.input_type) if self.input_type else "Input"
        else:
            first = {"CONTEXT": "Context", "DATA": "Blend File"}.get(self.root, "Data")
        result = [(first, 0)]
        keys = iter(self.keys)
        for count, (part, step) in enumerate(zip(self.parts, self.steps()), 1):
            if part == rna.SUBSCRIPT:
                result.append((next(keys).label(), count))
            else:
                result.append((rna.label(step), count))
        return result


class Unavailable(Exception):
    """The live data can't be reached (None on the way, no such item, ...)."""


# -----------------------------------------------------------------------------
# Live data
# -----------------------------------------------------------------------------


def evaluate(location: Location, context, count=None):
    """The live value at `location` (or at its first `count` segments).
    Raises Unavailable."""
    if location.root == "CONTEXT":
        value = context
    elif location.root == "DATA":
        value = bpy.data
    elif location.start is not None:
        value = location.start
    else:
        raise Unavailable("The data comes from a link")
    keys = iter(location.keys)
    steps = location.steps()
    for part, step in list(zip(location.parts, steps))[:count]:
        if value is None:
            raise Unavailable("Nothing there (None)")
        if part != rna.SUBSCRIPT:
            try:
                value = getattr(value, part)
            except AttributeError:
                raise Unavailable(f"No '{part}' here") from None
            continue
        key = next(keys)
        if key.mode == "ACTIVE":
            value = getattr(value, "active", None)
            if value is None:
                raise Unavailable("No active item")
        elif key.value is None:
            raise Unavailable("The item comes from a link")
        else:
            try:
                value = value[key.value]
            except (KeyError, IndexError, TypeError):
                raise Unavailable(f"No item {key.label()}") from None
    return value


def is_struct(value) -> bool:
    return isinstance(value, bpy.types.bpy_struct)


def is_collection(value) -> bool:
    return isinstance(value, bpy.types.bpy_prop_collection)


def item_key(collection, index, item) -> Key:
    """Key picking `item`: by name where items are found by name."""
    name = getattr(item, "name", None)
    if isinstance(name, str) and name:
        try:
            if collection[name] == item:
                return Key("NAME", name)
        except (KeyError, TypeError):
            pass
    return Key("INDEX", index)


def struct_members(value, context):
    """(identifier, label, property or None) of a struct's members. The
    context also has members that aren't RNA properties (active_object, ...)."""
    result = [
        (prop.identifier, prop.name or prop.identifier, prop)
        for prop in value.bl_rna.properties
        if prop.identifier != "rna_type"
    ]
    if isinstance(value, bpy.types.Context):
        known = {identifier for identifier, _, _ in result}
        for name in rna.CONTEXT_MEMBERS:
            if name not in known:
                result.append((name, name.replace("_", " ").title(), None))
    return result


# -----------------------------------------------------------------------------
# Locations of nodes and of the explorer itself
# -----------------------------------------------------------------------------


def follows(node) -> bool:
    """Nodes the explorer follows: Blender Data nodes, and property nodes in
    Blender mode."""
    from ..nodes._blend_path import BlendPathMixin

    return (
        isinstance(node, BlendPathMixin)
        and getattr(node, "mode", "BLENDER") == "BLENDER"
    )


def node_location(node, context) -> Location:
    """Where `node`'s path ends, with the keys it uses."""
    parts = node.path_parts() or []
    keys = []
    for index in range(parts.count(rna.SUBSCRIPT)):
        mode = node.path_keys[index].mode if index < len(node.path_keys) else "INDEX"
        socket = node.socket(f"key_{index}")
        if mode == "ACTIVE":
            keys.append(Key("ACTIVE"))
        elif socket is None or socket.is_linked:
            keys.append(Key(mode))
        else:
            keys.append(Key(mode, socket.value))
    input_type, start = "", None
    if node.path_root == "INPUT":
        input_type = node.path_root_step().rna_type
        start = _input_value(node, context)
    return Location(node.path_root, parts, keys, input_type, start)


def _input_value(node, context, depth=0):
    """Live data at the node's Data input, if it comes from a Blender Data
    node the explorer can evaluate."""
    socket = node.socket("data")
    if socket is None or not socket.is_linked or depth > 32:
        return None
    upstream = socket.links[0].from_node
    while upstream.bl_idname == "NodeReroute":
        if not upstream.inputs[0].is_linked:
            return None
        upstream = upstream.inputs[0].links[0].from_node
    if upstream.bl_idname != "SNA_Node_BlendData":
        return None
    location = node_location(upstream, context)
    if upstream.path_root == "INPUT":
        location.start = _input_value(upstream, context, depth + 1)
    try:
        return evaluate(location, context)
    except Unavailable:
        return None


def free_location(text) -> Location:
    """The explorer's own location from its stored Python path."""
    if not text:
        return Location("")
    if text in {"bpy.context", "bpy.data"}:
        return Location("CONTEXT" if text == "bpy.context" else "DATA")
    try:
        parsed = rna.parse(text)
    except ValueError:
        return Location("")
    keys = [Key("INDEX" if isinstance(k, int) else "NAME", k) for k in parsed.keys]
    return Location(parsed.root, parsed.segments, keys)


def set_node_location(node, location: Location):
    """Point `node`'s path at `location` (same root)."""
    node.path = rna.join(location.parts)
    node.sync_sockets()
    for index, key in enumerate(location.keys):
        if index >= len(node.path_keys):
            break
        node.path_keys[index].mode = key.mode
    node.sync_sockets()
    for index, key in enumerate(location.keys):
        socket = node.socket(f"key_{index}")
        if socket is not None and key.value is not None and not socket.is_linked:
            socket.value = key.value
    node.mark_dirty()
