"""The add-on's `__init__.py`: imports its modules and registers their
classes, the way add-ons are written by hand.

    from . import interface, operators, properties

    classes = (
        properties.MY_ADDON_PG_item,
        operators.MY_ADDON_OT_say_hello,
        interface.MY_ADDON_PT_main,
    )


    def register():
        for cls in classes:
            bpy.utils.register_class(cls)
        properties.register()
        interface.register()


    def unregister():
        interface.unregister()
        properties.unregister()
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)

The classes and hooks are read from the generated modules: every top-level
class deriving from a `bpy.types` type is registered, modules that define
`register()` / `unregister()` have them called after (before) the classes.
Scripts that register their own classes run first (last).
"""

import ast
from typing import NamedTuple

# bpy.types a class can derive from to be registered
REGISTRABLE = {
    "AddonPreferences",
    "AssetShelf",
    "FileHandler",
    "Gizmo",
    "GizmoGroup",
    "Header",
    "KeyingSetInfo",
    "Macro",
    "Menu",
    "Node",
    "NodeSocket",
    "NodeTree",
    "Operator",
    "Panel",
    "PropertyGroup",
    "RenderEngine",
    "UIList",
}


class Module(NamedTuple):
    name: str  # as imported into __init__.py, e.g. "operators"
    path: str  # import path, e.g. "operators" or "scripts.helpers"
    source: str
    registers_itself: bool = False  # a script with its own register()


class _Parsed(NamedTuple):
    classes: list[str]
    deps: dict[str, set[str]]  # class -> classes it needs registered first
    register: bool
    unregister: bool


def source(modules: list[Module], header: str, bl_info: str | None = None) -> str:
    """`modules` in import order: scripts, properties, trees (dependencies
    first). `bl_info` for add-ons loaded the legacy way (the live add-on)."""
    parsed = {m.name: _parse(m.source) for m in modules}
    classes = _ordered_classes(
        [
            (m.name, parsed[m.name])
            for m in modules
            if not m.registers_itself and parsed[m.name] is not None
        ]
    )
    early = [m for m in modules if m.registers_itself]
    hooks = [
        m for m in modules if not m.registers_itself and parsed[m.name] is not None
    ]
    used = [
        m
        for m in modules
        if m.registers_itself
        or any(cls.startswith(m.name + ".") for cls in classes)
        or (parsed[m.name] and (parsed[m.name].register or parsed[m.name].unregister))
    ]

    lines = [header, ""]
    if bl_info:
        lines += [bl_info, ""]
    if classes:
        lines.append("import bpy")
        lines.append("")
    plain = sorted(m.name for m in used if "." not in m.path)
    if plain:
        lines.append(f"from . import {', '.join(plain)}")
    for m in sorted((m for m in used if "." in m.path), key=lambda m: m.path):
        package, _, name = m.path.rpartition(".")
        alias = f" as {m.name}" if name != m.name else ""
        lines.append(f"from .{package} import {name}{alias}")
    if classes:
        lines += ["", "classes = ("]
        lines += [f"    {cls}," for cls in classes]
        lines.append(")")

    register, unregister = [], []
    for m in early:
        register.append(f"{m.name}.register()")
    if classes:
        register += ["for cls in classes:", "    bpy.utils.register_class(cls)"]
    for m in hooks:
        if parsed[m.name].register:
            register.append(f"{m.name}.register()")
    for m in reversed(hooks):
        if parsed[m.name].unregister:
            unregister.append(f"{m.name}.unregister()")
    if classes:
        unregister += [
            "for cls in reversed(classes):",
            "    bpy.utils.unregister_class(cls)",
        ]
    for m in reversed(early):
        if _parse_hooks(m.source)[1]:
            unregister.append(f"{m.name}.unregister()")

    for name, body in (("register", register), ("unregister", unregister)):
        lines += ["", "", f"def {name}():"]
        lines += [f"    {line}" for line in body] or ["    pass"]
    return "\n".join(lines) + "\n"


def defines(source: str, name: str) -> bool:
    """`source` defines a top-level function `name`."""
    register, unregister = _parse_hooks(source)
    return {"register": register, "unregister": unregister}.get(name, False)


def _parse_hooks(source):
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False, False
    names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    return "register" in names, "unregister" in names


def _parse(source) -> _Parsed | None:
    """Classes to register of a module, None if it doesn't parse (the
    syntax error is reported when the add-on is loaded)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    # names of bpy types: `from bpy.types import Panel`, and classes
    # deriving from them
    types = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "bpy.types":
            types |= {a.asname or a.name for a in node.names if a.name in REGISTRABLE}
    classes, deps = [], {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if any(_is_bpy_type(base, types) for base in node.bases):
            types.add(node.name)
            classes.append(node.name)
            deps[node.name] = _needs(node)
    functions = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    return _Parsed(classes, deps, "register" in functions, "unregister" in functions)


def _is_bpy_type(base, names):
    """`bpy.types.Operator`, `Panel` imported from bpy.types, a class
    deriving from one, ..."""
    if isinstance(base, ast.Name):
        return base.id in names
    return (
        isinstance(base, ast.Attribute)
        and base.attr in REGISTRABLE
        and isinstance(base.value, ast.Attribute)
        and base.value.attr == "types"
        and isinstance(base.value.value, ast.Name)
        and base.value.value.id == "bpy"
    )


def _needs(cls) -> set[str]:
    """Names of classes `cls` refers to that must be registered before it:
    `type=` of its properties, the `bl_parent_id` of a panel."""
    found = set()
    for node in ast.walk(cls):
        if isinstance(node, ast.keyword) and node.arg == "type":
            value = node.value
            if isinstance(value, ast.Attribute):
                found.add(value.attr)
            elif isinstance(value, ast.Name):
                found.add(value.id)
        elif (
            isinstance(node, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == "bl_parent_id" for t in node.targets
            )
            and isinstance(node.value, ast.Constant)
        ):
            found.add(str(node.value.value))
    return found


def _ordered_classes(modules) -> list[str]:
    """`module.Class` of all classes, in module order, moved after the
    classes they need."""
    entries = [(name, cls) for name, parsed in modules for cls in parsed.classes]
    deps = {cls: parsed.deps[cls] for _, parsed in modules for cls in parsed.classes}
    known = {cls for _, cls in entries}
    done, ordered = set(), []

    def visit(module, cls, path=()):
        if cls in done or cls in path:
            return
        for dep in sorted(deps[cls] & known):
            owner = next(m for m, c in entries if c == dep)
            visit(owner, dep, (*path, cls))
        done.add(cls)
        ordered.append(f"{module}.{cls}")

    for module, cls in entries:
        visit(module, cls)
    return ordered
