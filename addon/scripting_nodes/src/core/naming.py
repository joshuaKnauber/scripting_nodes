"""Names in the generated add-on: modules, classes, operator idnames,
functions. Readable (from labels) and unique, a suffix only on collision.

Nodes declare the names they define:

    def sn_names(self):
        label = naming.label(self)
        return [naming.Class("class", "OT", label), naming.Idname("idname", label)]

and read them with `ctx.name("class")` (or `naming.name(node, "idname")`
from other nodes and the UI). All names of the add-on are claimed in one
pass, trees by name and nodes by name, so a build always gives the same
names and every caller agrees on them.
"""

import builtins
import keyword
import re
from typing import NamedTuple

import bpy

# what's already taken at module level of every generated module
RESERVED_SYMBOLS = (
    set(keyword.kwlist)
    | set(dir(builtins))
    | {"bpy", "register", "unregister", "persistent", "atexit", "math"}
    | {"self", "context", "layout", "event"}
)
RESERVED_MODULES = set(keyword.kwlist) | {"auto_load", "addon", "properties"}


def addon_settings():
    return bpy.context.scene.sna.addon


def identifier(text: str, fallback: str = "item") -> str:
    """A valid Python identifier made from user text."""
    text = re.sub(r"[^a-zA-Z0-9_]", "_", text or "")
    text = re.sub(r"_+", "_", text).strip("_")
    if not text:
        text = fallback
    if text[0].isdigit():
        text = "_" + text
    return text


def snake(text: str, fallback: str = "item") -> str:
    """`My Value` -> `my_value`."""
    return identifier((text or "").lower(), fallback)


def label(node, socket="label", fallback=None) -> str:
    """What a node is called: its custom label, else the value of its label
    input (if not connected), else `fallback` or its type's name."""
    if node.label:
        return node.label
    input_ = node.socket(socket) if socket else None
    if input_ is not None and not input_.is_linked and getattr(input_, "value", ""):
        return input_.value
    return fallback or node.bl_label


# -- declarations ---------------------------------------------------------------


class Name(NamedTuple):
    key: str
    space: str  # "symbol", "idname" or "module"
    base: str
    kind: str = ""  # class names: OT, PT, MT, PG, AP


def Class(key, kind, text):
    """A class name, e.g. `MY_ADDON_OT_say_hello`."""
    return Name(key, "symbol", snake(text), kind)


def Idname(key, text):
    """An operator bl_idname, e.g. `my_addon.say_hello`."""
    return Name(key, "idname", snake(text))


def Symbol(key, base):
    """A module level function or variable name (used as is if valid)."""
    private = base.startswith("_")
    name = identifier(base, "value")
    return Name(key, "symbol", "_" + name if private else name)


# -- the registry -----------------------------------------------------------------


class Names:
    def __init__(self, prefix, namespace):
        self.prefix = prefix
        self.namespace = namespace
        self._names: dict[tuple[str, str], str] = {}
        self.used = {
            "symbol": set(RESERVED_SYMBOLS),
            "module": set(RESERVED_MODULES),
            "idname": set(),
        }

    def claim(self, owner_id, name: Name) -> str:
        key = (owner_id, name.key)
        if key in self._names:
            return self._names[key]
        base = name.base
        if name.kind:
            base = f"{self.prefix}_{name.kind}_{base}"
        elif name.space == "idname":
            base = f"{self.namespace}.{base}"
        result = unique(base, self.used[name.space])
        self._names[key] = result
        return result

    def get(self, owner_id, key):
        return self._names.get((owner_id, key))


def unique(base, used: set) -> str:
    """`base`, else `base_2`, `base_3`, ... Adds the result to `used`."""
    name, i = base, 2
    while name in used:
        name, i = f"{base}_{i}", i + 1
    used.add(name)
    return name


def build(trees=None, settings=None) -> Names:
    """Claim every name of the add-on, in a fixed order."""
    from ..lib.trees import scripting_node_trees, sn_nodes
    from . import functions, properties

    trees = sorted(
        trees if trees is not None else scripting_node_trees(), key=lambda t: t.name
    )
    settings = settings or addon_settings()
    names = Names(settings.class_prefix, settings.idname_namespace)
    for tree in trees:
        names.claim(tree.id, Name("module", "module", snake(tree.name, "tree")))
        if functions.is_function(tree):
            names.claim(tree.id, Symbol("function", snake(tree.name, "function")))
    properties.claim_names(names)
    for tree in trees:
        for node in sorted(sn_nodes(tree), key=lambda n: n.name):
            for name in node.sn_names():
                names.claim(node.id, name)
    return names


_current: Names | None = None


def use(names: Names):
    """Names of the build that's being compiled (and of the last one)."""
    global _current
    _current = names


def name(owner, key) -> str:
    """The name `owner` (node or tree) declared as `key`."""
    global _current
    if _current is None or _current.get(owner.id, key) is None:
        _current = build()  # changed since the last build (UI, tests)
    result = _current.get(owner.id, key)
    if result is None:
        raise KeyError(f"'{owner.name}' declares no name '{key}'")
    return result


def current() -> Names:
    global _current
    if _current is None:
        _current = build()
    return _current
