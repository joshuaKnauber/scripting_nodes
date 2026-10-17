"""Blender's data model from RNA type information, independent of the open file.

A data path is a root plus segments: `objects[].modifiers[].show_viewport`
from root `DATA` is `bpy.data.objects[...].modifiers[...].show_viewport`.
`[]` is a subscript whose key comes from an input of the node.

    steps = resolve("BlendData", segments("objects[].name"))
    steps[-1].prop.type  -> "STRING"
"""

import re
from dataclasses import dataclass
from functools import lru_cache

import bpy

from ..sockets import spec
from ..sockets.data.socket_string import encode_enum_items

# context members that aren't RNA properties of bpy.types.Context:
# name -> (struct type, is collection)
CONTEXT_MEMBERS = {
    "active_object": ("Object", False),
    "object": ("Object", False),
    "edit_object": ("Object", False),
    "pose_object": ("Object", False),
    "selected_objects": ("Object", True),
    "selected_editable_objects": ("Object", True),
    "visible_objects": ("Object", True),
    "selectable_objects": ("Object", True),
    "editable_objects": ("Object", True),
    "objects_in_mode": ("Object", True),
    "active_bone": ("Bone", False),
    "active_pose_bone": ("PoseBone", False),
    "selected_pose_bones": ("PoseBone", True),
    "selected_bones": ("EditBone", True),
    "selected_editable_bones": ("EditBone", True),
    "material": ("Material", False),
    "material_slot": ("MaterialSlot", False),
    "mesh": ("Mesh", False),
    "camera": ("Camera", False),
    "light": ("Light", False),
    "world": ("World", False),
    "active_node": ("Node", False),
    "selected_nodes": ("Node", True),
    "active_action": ("Action", False),
    "active_operator": ("Operator", False),
    "active_strip": ("Strip", False),
    "edit_image": ("Image", False),
    "active_file": ("FileSelectEntry", False),
    "selected_files": ("FileSelectEntry", True),
    "selected_ids": ("ID", True),
    "id": ("ID", False),
}

ROOT_TYPES = {"CONTEXT": "Context", "DATA": "BlendData"}
ROOT_EXPRESSIONS = {"DATA": "bpy.data"}  # CONTEXT depends on the scope

SUBSCRIPT = "[]"
_IDENTIFIER = r"[A-Za-z_][A-Za-z0-9_]*"
_PATH = re.compile(
    rf"(?:\[\])*(?:{_IDENTIFIER}(?:\[\])*(?:\.{_IDENTIFIER}(?:\[\])*)*)?"
)


def is_identifier(name: str) -> bool:
    """True for a plain Python attribute name like `frame_end`."""
    return bool(re.fullmatch(_IDENTIFIER, name or ""))


# -----------------------------------------------------------------------------
# Types
# -----------------------------------------------------------------------------


def struct(name):
    """RNA struct of a type name, or None."""
    cls = getattr(bpy.types, name, None) if name else None
    rna = getattr(cls, "bl_rna", None)
    return rna if isinstance(rna, bpy.types.Struct) else None


def display_name(type_name: str) -> str:
    """ "ViewLayer" -> "View Layer" (the struct's UI name)."""
    rna = struct(type_name)
    return rna.name if rna and rna.name else type_name


@lru_cache(maxsize=None)
def _all_structs():
    names = []
    for name in dir(bpy.types):
        if struct(name) is not None:
            names.append(name)
    return tuple(names)


@lru_cache(maxsize=None)
def subtypes(type_name: str) -> tuple:
    """Types derived from `type_name` (Mesh, Curve, ... for ID)."""
    if not type_name:
        return ()
    found = []
    for name in _all_structs():
        base = struct(name).base
        while base is not None:
            if base.identifier == type_name:
                found.append(name)
                break
            base = base.base
    return tuple(sorted(found))


def all_types() -> list[str]:
    return sorted(n for n in _all_structs() if not n.startswith(("SNA_", "SN_")))


# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Step:
    """What one segment of a path evaluates to."""

    name: str  # attribute name, or "[]"
    rna_type: str = ""  # struct type of the value ("" for plain values/unknown)
    collection: bool = False
    # struct of the collection itself (ObjectModifiers: .active, .new(), ...)
    collection_type: str = ""
    prop: object = None  # bpy.types.Property, None for subscripts/unknown
    known: bool = True

    @property
    def is_subscript(self):
        return self.name == SUBSCRIPT


UNKNOWN = Step("", known=False)


def segments(path: str) -> list[str]:
    """`objects[].name` -> ["objects", "[]", "name"]. Raises ValueError for
    anything that isn't a plain path (paths end up in generated code)."""
    if not path:
        return []
    if not _PATH.fullmatch(path):
        raise ValueError(f"Invalid data path: {path}")
    return re.findall(rf"\[\]|{_IDENTIFIER}", path)


def join(parts) -> str:
    text = ""
    for part in parts:
        if part == SUBSCRIPT or not text:
            text += part
        else:
            text += "." + part
    return text


def _step_for_prop(prop) -> Step:
    if prop.type in {"POINTER", "COLLECTION"}:
        fixed = getattr(prop, "fixed_type", None)
        srna = getattr(prop, "srna", None)
        return Step(
            prop.identifier,
            rna_type=fixed.identifier if fixed else "",
            collection=prop.type == "COLLECTION",
            collection_type=srna.identifier if srna else "",
            prop=prop,
        )
    return Step(prop.identifier, prop=prop)


def member(owner: Step, name: str) -> Step:
    """Attribute `name` of a value described by `owner`."""
    if not owner.known:
        return Step(name, known=False)
    type_name = owner.collection_type if owner.collection else owner.rna_type
    rna = struct(type_name)
    if rna is not None:
        prop = rna.properties.get(name)
        if prop is not None and name != "rna_type":
            return _step_for_prop(prop)
    if owner.rna_type == "Context" and name in CONTEXT_MEMBERS:
        type_name, collection = CONTEXT_MEMBERS[name]
        return Step(name, rna_type=type_name, collection=collection)
    if not owner.collection:
        # a property of a more specific type: `width` of a modifier is
        # BevelModifier.width
        for subtype in subtypes(type_name):
            prop = struct(subtype).properties.get(name)
            if prop is not None:
                return _step_for_prop(prop)
    return Step(name, known=False)


def item(owner: Step) -> Step:
    """What subscripting `owner` gives: a collection's item, else unknown
    (custom properties like `object["prop"]`)."""
    if owner.known and owner.collection:
        return Step(SUBSCRIPT, rna_type=owner.rna_type)
    return Step(SUBSCRIPT, known=False)


def resolve(root: Step, parts: list[str]) -> list[Step]:
    """One Step per segment, starting from `root`."""
    steps = []
    current = root
    for part in parts:
        current = item(current) if part == SUBSCRIPT else member(current, part)
        steps.append(current)
    return steps


def root_step(type_name: str, collection=False) -> Step:
    if not type_name:
        return UNKNOWN
    return Step("", rna_type=type_name, collection=collection)


def members(owner: Step) -> list[Step]:
    """Everything accessible on `owner` (attributes, plus `[]` for
    collections)."""
    if not owner.known:
        return []
    if owner.collection:
        return [item(owner)]
    rna = struct(owner.rna_type)
    found = []
    if rna is not None:
        found = [
            _step_for_prop(p) for p in rna.properties if p.identifier != "rna_type"
        ]
    if owner.rna_type == "Context":
        for name, (type_name, collection) in CONTEXT_MEMBERS.items():
            found.append(Step(name, rna_type=type_name, collection=collection))
    return found


def label(step: Step) -> str:
    """UI name of a step: the property's name, or the item type."""
    if step.is_subscript or not step.name:  # an item, or the root
        return display_name(step.rna_type) if step.rna_type else "Item"
    # context members are named like their identifier ("scene")
    if step.prop is not None and step.prop.name and step.prop.name != step.name:
        return step.prop.name
    return step.name.replace("_", " ").title()


def type_label(step: Step) -> str:
    """ "Object", "Objects" (collection), "Float", ... for tooltips/search."""
    if step.rna_type:
        name = display_name(step.rna_type)
        return f"Collection of {name}" if step.collection else name
    if step.prop is not None:
        return step.prop.type.title()
    return ""


# -----------------------------------------------------------------------------
# Sockets
# -----------------------------------------------------------------------------


def blend_data_spec(key, label_text, type_name, collection=False, **kwargs):
    """A Blender Data socket typed with `type_name` ("" = any)."""
    description = ""
    if type_name:
        name = display_name(type_name)
        description = f"Collection of {name}" if collection else name
    return spec.BlendData(
        key,
        label_text,
        blend_type=type_name,
        collection=collection,
        description=description,
        **kwargs,
    )


def value_spec(step: Step, key: str, label_text: str):
    """The socket for values of `step`."""
    if not step.known:
        return spec.Data(key, label_text)
    if step.rna_type or step.collection:
        return blend_data_spec(key, label_text, step.rna_type, step.collection)
    prop = step.prop
    if prop is None:
        return spec.Data(key, label_text)
    size = getattr(prop, "array_length", 0) if prop.type != "STRING" else 0
    if prop.type in {"FLOAT", "INT", "BOOLEAN"} and size:
        if prop.type == "FLOAT" and prop.subtype in {"COLOR", "COLOR_GAMMA"}:
            if size in (3, 4):
                return spec.Color(key, label_text, alpha=size == 4)
        if prop.type != "BOOLEAN" and 2 <= size <= 4:
            return spec.Vector(key, label_text, dimension=size)
        return spec.List(key, label_text)
    if prop.type == "BOOLEAN":
        return spec.Boolean(key, label_text)
    if prop.type == "INT":
        return spec.Integer(key, label_text)
    if prop.type == "FLOAT":
        return spec.Float(key, label_text)
    if prop.type == "STRING":
        return spec.String(key, label_text)
    if prop.type == "ENUM":
        if prop.is_enum_flag:
            return spec.Data(key, label_text)  # a set of identifiers
        items = [(i.identifier, i.name) for i in prop.enum_items]
        return spec.String(
            key, label_text, enum_items=encode_enum_items(items) if items else None
        )
    return spec.Data(key, label_text)


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------


def functions(owner: Step) -> list:
    """Functions that can be called on a value described by `owner`
    (`modifiers.new()` is a function of the collection), by name. Blender's
    callbacks (a panel's `draw`) and functions without `self` aren't."""
    if not owner.known:
        return []
    rna = struct(owner.collection_type if owner.collection else owner.rna_type)
    if rna is None:
        return []
    return [
        function
        for function in rna.functions
        if function.use_self
        and not function.is_registered
        and not function.is_registered_optional
        and not function.identifier.startswith("bl_")
    ]


def function(owner: Step, name: str):
    """Function `name` of `owner` (functions()), or None."""
    return next((f for f in functions(owner) if f.identifier == name), None)


def function_label(function) -> str:
    """ "new()", the way the browser and the node show it."""
    return f"{function.identifier}()"


def parameters(function, outputs=False) -> list:
    """The function's parameters, or what it returns."""
    return [p for p in function.parameters if p.is_output == outputs]


def parameter_step(parameter) -> Step:
    """What a parameter or result of a function is, like a property's step."""
    return _step_for_prop(parameter)


def parameter_spec(parameter, key: str):
    """The socket of a function's parameter or result, with its default."""
    step = parameter_step(parameter)
    label_text = parameter.name or parameter.identifier.replace("_", " ").title()
    socket = value_spec(step, key, label_text)
    default = parameter_default(parameter)
    if default is not None and not parameter.is_output:
        socket.default = default
    return socket


def parameter_default(parameter):
    """The default of a plain value parameter (None for data)."""
    if parameter.type in {"POINTER", "COLLECTION"}:
        return None
    if parameter.type == "ENUM":
        if parameter.is_enum_flag:
            return None
        return parameter.default or None
    if getattr(parameter, "array_length", 0) and parameter.type != "STRING":
        return tuple(parameter.default_array)
    return parameter.default


# -----------------------------------------------------------------------------
# Search
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Entry:
    path: str
    text: str  # "Render › FPS"
    type_label: str
    final: Step
    haystack: str


# context members most addons start from: ranked first in the search
COMMON_CONTEXT = {
    "scene",
    "active_object",
    "selected_objects",
    "view_layer",
    "preferences",
    "window_manager",
    "tool_settings",
    "space_data",
}


def _entry(parts, labels, step):
    text = " › ".join(labels)
    path = join(parts)
    haystack = f"{path} {text}".lower().replace("_", " ")
    return Entry(path, text, type_label(step), step, haystack)


@lru_cache(maxsize=64)
def _entries(type_name: str, collection: bool, depth: int) -> tuple:
    """Every path reachable from a root type within `depth` attributes
    (subscripts don't count), breadth first. Each type is expanded once, at
    its shortest path, so this stays small."""
    entries = []
    expanded = {(type_name, collection)}
    root = root_step(type_name, collection)
    frontier = [((), (), root)]
    if collection:  # the items of a collection root
        item_step = item(root)
        entries.append(_entry(("[]",), ("Item[]",), item_step))
        frontier = [(("[]",), ("Item[]",), item_step)]
    for _ in range(depth):
        next_frontier = []
        for parts, labels, owner in frontier:
            for step in members(owner):
                step_parts = parts + (step.name,)
                step_labels = labels + (label(step),)
                entries.append(_entry(step_parts, step_labels, step))
                if step.collection:
                    # "Modifiers[] › Name": items are one level with the collection
                    step = item(step)
                    step_parts += (SUBSCRIPT,)
                    step_labels = labels + (step_labels[-1] + "[]",)
                    entries.append(_entry(step_parts, step_labels, step))
                key = (step.rna_type, step.collection)
                if step.rna_type and key not in expanded:
                    expanded.add(key)
                    next_frontier.append((step_parts, step_labels, step))
        frontier = next_frontier
    return tuple(entries)


def _scope(root: Step, query: str):
    """`active_object.active_mat` -> the part before the last dot (as parts
    and steps from `root`) and the rest. Searching from where that part
    leads finds every path through it, not only the ones `_entries` keeps.
    ((), (), query) when there's no dot or the part doesn't lead to data."""
    head, dot, rest = query.rpartition(".")
    if not dot:
        return (), (), query
    try:
        parts = segments(re.sub(r"\[[^\]]*\]", SUBSCRIPT, head.strip()))
    except ValueError:
        return (), (), query
    steps = resolve(root, parts)
    last = steps[-1] if steps else UNKNOWN
    if not last.known or not (last.rna_type or last.collection):
        return (), (), query
    return tuple(parts), tuple(steps), rest


def _with_prefix(entry: Entry, parts, steps) -> Entry:
    """`entry` (found from where `parts` lead) as a path from the root."""
    labels = []
    for step in steps:  # "Modifiers[]" like in _entries
        if step.is_subscript and labels:
            labels[-1] += SUBSCRIPT
        else:
            labels.append(label(step))
    rest = entry.text.split(" › ")
    path = join(parts)
    if entry.path.startswith(SUBSCRIPT):  # items of a collection: no "Item[]"
        labels[-1] += SUBSCRIPT
        rest = rest[1:]
        path += entry.path
    else:
        path += "." + entry.path
    return Entry(
        path, " › ".join(labels + rest), entry.type_label, entry.final, entry.haystack
    )


def _names(entry: Entry, word: str) -> bool:
    """Whether `word` is in the last part of `entry` (its name or label)."""
    name = entry.path.rsplit(".", 1)[-1].replace("_", " ").lower()
    text = entry.text.rsplit(" › ", 1)[-1].lower()
    return word in name or word in text


def search(root: Step, query: str, accept=None, depth=3, limit=200) -> list[Entry]:
    """Paths from `root` matching all words of `query`, best first.
    `accept(step)` filters the final steps (e.g. only booleans); data that
    leads further is still offered when its name matches the last word, so
    it can be picked and searched on (`active_object.active_material.`).
    A query with dots searches from where the part before the last dot
    leads."""
    if not root.known:
        return []
    parts, steps, rest = _scope(root, query)
    start = steps[-1] if steps else root
    entries = _entries(start.rna_type, start.collection, depth)
    words = rest.lower().replace("_", " ").replace(".", " ").split()
    last_word = rest.rsplit(".", 1)[-1].lower()
    scored = []
    for entry in entries:
        if not all(word in entry.haystack for word in words):
            continue
        # the last word names what's found, not data on the way to it: "parti"
        # finds Particle Systems, not everything inside them
        if words and not _names(entry, words[-1]):
            continue
        score = entry.path.count(".")
        if accept is not None and not accept(entry.final):
            name = entry.path.rsplit(".", 1)[-1]
            if not (last_word and entry.final.rna_type and name.startswith(last_word)):
                continue
            score += 0.5  # after values named the same
        last = entry.text.rsplit(" › ", 1)[-1].lower().rstrip("[]")
        if words and last.startswith(words[-1]):
            score -= 2
        if words and last == " ".join(words):
            score -= 3
        if (
            not steps
            and root.rna_type == "Context"
            and entry.path.split(".")[0] in COMMON_CONTEXT
        ):
            score -= 0.5
        scored.append((score, entry.path, entry))
    scored.sort(key=lambda s: (s[0], s[1]))
    found = [entry for _, _, entry in scored[:limit]]
    if steps:
        found = [_with_prefix(entry, parts, steps) for entry in found]
    return found


# -----------------------------------------------------------------------------
# Pasted paths
# -----------------------------------------------------------------------------


@dataclass
class ParsedPath:
    root: str  # CONTEXT, DATA or INPUT
    segments: list
    keys: list  # one per subscript: int index or str name
    input_type: str = ""  # INPUT: the type of the data the path starts at


_TOKEN = re.compile(
    rf"""\.?({_IDENTIFIER})          # attribute
       | \[\s*(-?\d+)\s*\]            # [0]
       | \[\s*"((?:[^"\\]|\\.)*)"\s*\]  # ["name"]
       | \[\s*'((?:[^'\\]|\\.)*)'\s*\]  # ['name']
    """,
    re.VERBOSE,
)


def parse(text: str) -> ParsedPath:
    """A copied Python path (`bpy.context.scene.render.fps`,
    `bpy.data.objects["Cube"].location`, `bpy.types.Object.location`).
    Raises ValueError for anything else."""
    text = (text or "").strip()
    for prefix, root in (
        ("bpy.context.", "CONTEXT"),
        ("context.", "CONTEXT"),
        ("bpy.data.", "DATA"),
        ("bpy.types.", "INPUT"),
    ):
        if text.startswith(prefix):
            rest = text[len(prefix) :]
            break
    else:
        raise ValueError("Not a Blender data path (bpy.context..., bpy.data...)")

    parts, keys = [], []
    position = 0
    while position < len(rest):
        match = _TOKEN.match(rest, position)
        attribute, index, double, single = match.groups() if match else (None,) * 4
        # attributes are dotted, except the first one
        dotted = bool(match) and match.group(0).startswith(".")
        if match is None or (attribute is not None and dotted != (position > 0)):
            raise ValueError(f"Can't read the path at '{rest[position:]}'")
        if attribute is not None:
            parts.append(attribute)
        else:
            parts.append(SUBSCRIPT)
            if index is not None:
                keys.append(int(index))
            else:
                name = double if double is not None else single
                keys.append(re.sub(r"\\(.)", r"\1", name))
        position = match.end()
    if not parts:
        raise ValueError("The path is empty")

    input_type = ""
    if root == "INPUT":
        input_type = parts.pop(0)
        if struct(input_type) is None:
            raise ValueError(f"Unknown type: {input_type}")
    return ParsedPath(root, parts, keys, input_type)


# bpy.data collection -> context member holding its active item
_ACTIVE_IN_CONTEXT = {
    "scenes": "scene",
    "objects": "active_object",
    "screens": "screen",
    "window_managers": "window_manager",
    "workspaces": "workspace",
}


def prefer_context(parsed: ParsedPath, context) -> ParsedPath:
    """Blender copies `bpy.data.scenes["Scene"].render.fps` even for the
    active scene; an addon almost always means `context.scene.render.fps`."""
    if parsed.root != "DATA" or len(parsed.segments) < 2:
        return parsed
    collection, subscript = parsed.segments[:2]
    member_name = _ACTIVE_IN_CONTEXT.get(collection)
    if (
        member_name is None
        or subscript != SUBSCRIPT
        or not isinstance(parsed.keys[0], str)
    ):
        return parsed
    active = getattr(context, member_name, None)
    if active is None or getattr(active, "name", None) != parsed.keys[0]:
        return parsed
    return ParsedPath("CONTEXT", [member_name] + parsed.segments[2:], parsed.keys[1:])
