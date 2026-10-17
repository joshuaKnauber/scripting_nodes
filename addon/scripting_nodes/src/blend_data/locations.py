"""Locations in Blender's data, for the path browser (blend_data/browser.py).

A Location is a path with concrete keys, like a Blender Data node's path:

    Location("CONTEXT", ["active_object", "modifiers", "[]"], [Key("NAME", "Bevel")])

The browser stores its location as a Python path (`free_location`).
`node_location` / `absolute_location` read a node's path, `apply_to_node`
sets it. `evaluate()` walks a location through the live data; where that
isn't possible (nothing active right now) the browser falls back to the
types (rna.py), without values.
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
                self.root,
                self.parts + [rna.SUBSCRIPT],
                self.keys + [key],
                self.input_type,
            )
        return Location(
            self.root, self.parts + [name], list(self.keys), self.input_type
        )

    def truncated(self, count) -> "Location":
        """The first `count` segments of this location."""
        parts = self.parts[:count]
        keys = self.keys[: parts.count(rna.SUBSCRIPT)]
        return Location(self.root, parts, keys, self.input_type)

    def python(self) -> str:
        """`bpy.context.active_object.modifiers["Bevel"]`; a location from
        the Data input as `bpy.types.Object.modifiers[0]` (rna.parse)."""
        if self.root == "INPUT":
            text = f"bpy.types.{self.input_type}" if self.input_type else "bpy.types"
        else:
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
        (prop.identifier, _label(prop.identifier, prop.name), prop)
        for prop in value.bl_rna.properties
        if prop.identifier != "rna_type"
    ]
    if isinstance(value, bpy.types.Context):
        known = {identifier for identifier, _, _ in result}
        for name in rna.CONTEXT_MEMBERS:
            if name not in known:
                result.append((name, _label(name), None))
    return result


def _label(identifier, name=""):
    """The property's name; context members are named like their identifier
    ("window_manager")."""
    if name and name != identifier:
        return name
    return identifier.replace("_", " ").title()


# -----------------------------------------------------------------------------
# The browser's location, and nodes' paths
# -----------------------------------------------------------------------------


def free_location(text) -> Location:
    """The browser's location from its stored Python path ("" = the start)."""
    if not text:
        return Location("")
    roots = {"bpy.context": "CONTEXT", "bpy.data": "DATA", "bpy.types": "INPUT"}
    if text in roots:
        return Location(roots[text])
    try:
        parsed = rna.parse(text)
    except ValueError:
        return Location("")
    keys = [Key("INDEX" if isinstance(k, int) else "NAME", k) for k in parsed.keys]
    return Location(parsed.root, parsed.segments, keys, parsed.input_type)


def node_location(node) -> Location:
    """`node`'s own path with the keys it uses (root INPUT: relative to
    its Data input)."""
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
    input_type = node.path_root_step().rna_type if node.path_root == "INPUT" else ""
    return Location(node.path_root, parts, keys, input_type)


def _upstream(node):
    """The Blender Data node connected to `node`'s Data input, or None."""
    socket = node.socket("data")
    if socket is None or not socket.is_linked:
        return None
    upstream = socket.links[0].from_node
    while upstream.bl_idname == "NodeReroute":
        if not upstream.inputs[0].is_linked:
            return None
        upstream = upstream.inputs[0].links[0].from_node
    return upstream if upstream.bl_idname == "SNA_Node_BlendData" else None


def absolute_location(node, depth=0) -> Location:
    """Where `node`'s path ends, from Context or Blend File (following
    Blender Data nodes connected to its Data input). Raises Unavailable."""
    location = node_location(node)
    if any(key.mode != "ACTIVE" and key.value is None for key in location.keys):
        raise Unavailable("A key of its path comes from a link")
    if location.root != "INPUT":
        return location
    upstream = _upstream(node)
    if upstream is None or depth > 32:
        raise Unavailable("Its path starts at data from a link")
    base = absolute_location(upstream, depth + 1)
    return Location(base.root, base.parts + location.parts, base.keys + location.keys)


def apply_to_node(node, location: Location):
    """Point `node`'s path at `location`. A node starting at its Data input
    keeps that start if `location` continues from there; a location from
    the Data input (root INPUT) makes it start there."""
    if location.root == "INPUT":
        node.path_root = "INPUT"
        if location.input_type and not linked_type(node):
            node.path_input_type = location.input_type
        set_node_location(node, location)
        return
    if node.path_root == "INPUT":
        upstream = _upstream(node)
        try:
            base = absolute_location(upstream) if upstream is not None else None
        except Unavailable:
            base = None
        if base is not None and continues(location, base):
            tail = Location(
                "INPUT", location.parts[len(base.parts):], location.keys[len(base.keys):]
            )  # fmt: skip
            set_node_location(node, tail)
            return
        socket = node.socket("data")
        for link in list(socket.links) if socket is not None else ():
            node.id_data.links.remove(link)
    node.path_root = location.root
    set_node_location(node, location)


def linked_type(node) -> str:
    """The type of the data connected to `node`'s Data input ("" if none)."""
    from ..sockets.data.socket_blend_data import linked_rna_type

    socket = node.socket("data")
    return linked_rna_type(socket)[0] if socket is not None else ""


def input_location(node) -> Location:
    """Where `node`'s Data input leads: the upstream Blender Data node's
    path (live data), else the input's type."""
    upstream = _upstream(node) if node.path_root == "INPUT" else None
    if upstream is not None:
        try:
            return absolute_location(upstream)
        except Unavailable:
            pass
    type_name = linked_type(node) or node.path_input_type
    return Location("INPUT", input_type=type_name)


def continues(location, base) -> bool:
    """Whether `location` starts with `base`."""
    return (
        location.root == base.root
        and location.parts[: len(base.parts)] == base.parts
        and location.keys[: len(base.keys)] == base.keys
    )


def set_node_location(node, location: Location):
    """Set `node`'s path and keys from `location` (root unchanged)."""
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
