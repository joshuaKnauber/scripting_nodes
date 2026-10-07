"""Graph -> addon files. Pure: reads bpy data, writes nothing.

    compile_addon(dev=True) -> {"__init__.py": "...", "addon/<tree>.py": "...", ...}

Each tree becomes one module. Root nodes (operators, panels, events, ...) are
emitted first; everything else is emitted when a flow reaches it or when a
value it outputs is used. Nodes write through core/context.NodeContext.
"""

import hashlib
import os
import sys
import textwrap

import bpy

from ..lib.logger import log
from ..lib.sockets import to_socket
from ..lib.trees import scripting_node_trees, sn_nodes
from . import errors, helpers
from .context import Line, NodeContext, NodeError, Scope

TEMPLATES = os.path.join(os.path.dirname(__file__), "templates")
HELPERS_MODULE = "_sn_helpers"

# relpath -> owner node id per line, of the last live compile (error blame)
line_owners: dict[str, list] = {}
# node id -> its own generated lines, of the last live compile (code preview)
node_lines: dict[str, list[str]] = {}

_format_cache: dict[str, str] = {}
_FORMAT_CACHE_SIZE = 256


# -----------------------------------------------------------------------------
# Entry points
# -----------------------------------------------------------------------------


def compile_addon(dev=True, pretty=False, settings=None) -> dict[str, str]:
    """All files of the generated addon. Empty if there are no trees.

    `dev`: live addon (True) or export (False). `pretty`: run autopep8 over
    the tree modules (slow, export only)."""
    trees = scripting_node_trees()
    if not trees:
        return {}
    if settings is None:
        settings = bpy.context.scene.sna.addon
    errors.node_errors.clear()
    values = {"$ADDON_NAME": settings.addon_name, "$MODULE_NAME": settings.module_name}
    files = {
        "__init__.py": _render("init.txt", values),
        "auto_load.py": _render("auto_load.txt", values),
        "blender_manifest.toml": _render("blender_manifest.txt", values),
        "addon/__init__.py": "",
    }
    owners, previews, used_helpers = {}, {}, set()
    for tree in trees:
        builder = ModuleBuilder(tree, dev)
        source, line_map = builder.build()
        rel = f"addon/{tree.module_name}.py"
        files[rel] = _format(source) if pretty else source
        owners[rel] = line_map
        previews.update(_previews(source, line_map))
        used_helpers |= builder.helpers
    exported = {name for name in used_helpers if helpers.needs_import(name, dev)}
    if exported:
        files[f"{HELPERS_MODULE}.py"] = helpers.source(exported, dev)
    if dev and not pretty:
        line_owners.clear()
        line_owners.update(owners)
        node_lines.clear()
        node_lines.update(previews)
    return files


def compile_tree(tree, dev=True, pretty=True) -> str:
    """Python source of one tree module."""
    source, _ = ModuleBuilder(tree, dev).build()
    return _format(source) if pretty else source


# -----------------------------------------------------------------------------
# Module builder
# -----------------------------------------------------------------------------


class ModuleBuilder:
    """Collects the code of one tree module while its nodes emit."""

    def __init__(self, tree, dev):
        self.tree = tree
        self.dev = dev
        self.imports = {"import bpy"}
        self.blocks: list[list[Line]] = []
        self.register: list[Line] = []
        self.unregister: list[Line] = []
        self.helpers: set[str] = set()
        self._names: dict[str, int] = {}
        self._emitted: set[int] = set()

    # -- emission -----------------------------------------------------------

    def build(self):
        limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(limit, 20000))  # long flow chains recurse
        try:
            module_scope = Scope()
            roots = [n for n in sn_nodes(self.tree) if n.sn_root]
            roots.sort(key=lambda n: n.sn_order)
            for node in roots:
                self._emit(node, module_scope, "root")
            if self.tree.is_group:
                self.add_block(self._group_function(module_scope))
        finally:
            sys.setrecursionlimit(limit)
        return self._assemble()

    def _emit(self, node, scope, mode) -> NodeContext | None:
        ctx = NodeContext(self, node, scope, mode)
        self._emitted.add(node.as_pointer())
        try:
            node.emit(ctx)
        except NodeError as exc:
            errors.node_errors[node.id] = str(exc)
            return None
        except Exception as exc:
            errors.set_node_error(node.id, exc)
            log(
                "ERROR",
                f"'{node.name}' failed to generate code:\n"
                + errors.format_exception(exc),
            )
            return None
        return ctx

    def compile_flow(self, output_socket, scope) -> list[Line]:
        """Code of the node connected to a flow output (it emits the rest)."""
        target = to_socket(output_socket)
        if target is None:
            return []
        ctx = self._emit(target.node, scope, "statement")
        return ctx.lines() if ctx else []

    def evaluate(self, node, key, scope) -> str:
        """Expression of output `key` of a value node."""
        ctx = self._emit(node, scope, "value")
        if ctx is None:
            return "None"
        return ctx.outputs.get(key, "None")

    def add_block(self, lines):
        if any(line.text for line in lines):
            self.blocks.append(lines)

    # -- module services ------------------------------------------------------

    def unique_name(self, name):
        count = self._names.get(name, 0) + 1
        self._names[name] = count
        return f"{name}_{count}"

    def use_helper(self, name):
        if name not in helpers.HELPERS:
            raise NodeError(f"Unknown helper '{name}'")
        self.helpers.add(name)
        if helpers.needs_import(name, self.dev):
            self.imports.add(f"from ..{HELPERS_MODULE} import {name}")
        return helpers.call_name(name, self.dev)

    def import_symbol(self, owner, name):
        tree = owner if hasattr(owner, "nodes") else owner.id_data
        if tree != self.tree:
            self.imports.add(f"from .{tree.module_name} import {name}")
        return name

    # -- groups -------------------------------------------------------------

    def _group_function(self, module_scope) -> list[Line]:
        """A group tree compiles to `def <module_name>(params, *, self=None,
        context=None, layout=None, event=None)`."""
        group_input = group_output = None
        for node in sn_nodes(self.tree):
            if node.bl_idname == "SNA_Node_GroupInput" and group_input is None:
                group_input = node
            elif node.bl_idname == "SNA_Node_GroupOutput" and group_output is None:
                group_output = node

        params = group_input.parameter_names() if group_input else []
        implicit = ["self", "context", "layout", "event"]
        signature = ", ".join(params + ["*"] + [f"{n}=None" for n in implicit])
        values = {}
        if group_input:
            for key, name in zip(group_input.parameter_keys(), params):
                values[(group_input.as_pointer(), key)] = name
        scope = Scope(module_scope, "layout", values, frozenset(params + implicit))

        lines = [Line(0, f"def {self.tree.module_name}({signature}):", None)]
        lines.append(Line(4, "context = context or bpy.context", None))
        body = []
        if group_input:
            body = self.compile_flow(group_input.socket("function", output=True), scope)
        if group_output and group_output.as_pointer() not in self._emitted:
            ctx = self._emit(group_output, scope, "statement")
            body += ctx.lines() if ctx else []
        lines += [Line(4 + line.indent, line.text, line.owner) for line in body]
        return lines

    # -- assembly -------------------------------------------------------------

    def _assemble(self):
        blocks = [[Line(0, line, None) for line in sorted(self.imports)]]
        blocks += self.blocks
        for name, body in (
            ("register", self.register),
            ("unregister", self.unregister),
        ):
            function = [Line(0, f"def {name}():", None)]
            function += [Line(4 + line.indent, line.text, line.owner) for line in body]
            blocks.append(function)

        lines: list[Line] = []
        for i, block in enumerate(blocks):
            if i:
                lines += [Line(0, "", None), Line(0, "", None)]
            lines += block
        lines = _finalize(lines)
        source = "\n".join(" " * l.indent + l.text if l.text else "" for l in lines)
        return source + "\n", [l.owner for l in lines]


def _finalize(lines: list[Line]) -> list[Line]:
    """Add `pass` to empty blocks, drop `else:` branches that only pass."""
    result: list[Line] = []
    for i, line in enumerate(lines):
        result.append(line)
        text = line.text.rstrip()
        if text.endswith(":") and not text.lstrip().startswith("#"):
            following = next((l for l in lines[i + 1 :] if l.text), None)
            if following is None or following.indent <= line.indent:
                result.append(Line(line.indent + 4, "pass", line.owner))

    final: list[Line] = []
    i = 0
    while i < len(result):
        line = result[i]
        if line.text.strip() == "else:" and i + 1 < len(result):
            body = result[i + 1]
            after = next((l for l in result[i + 2 :] if l.text), None)
            if body.text.strip() == "pass" and (
                after is None or after.indent <= line.indent
            ):
                i += 2
                continue
        final.append(line)
        i += 1
    return final


def _previews(source, owners):
    """{node id: its own lines, dedented} for the code preview on nodes."""
    by_node: dict[str, list[str]] = {}
    for text, owner in zip(source.split("\n"), owners):
        if owner and text.strip():
            by_node.setdefault(owner, []).append(text)
    return {
        node_id: textwrap.dedent("\n".join(lines)).split("\n")
        for node_id, lines in by_node.items()
    }


def _render(template, values):
    with open(os.path.join(TEMPLATES, template)) as f:
        text = f.read()
    for key, value in values.items():
        text = text.replace(key, value)
    return text


def _format(code: str) -> str:
    key = hashlib.sha1(code.encode()).hexdigest()
    cached = _format_cache.get(key)
    if cached is not None:
        return cached
    try:
        import autopep8

        formatted = autopep8.fix_code(code, options={"aggressive": 1})
    except Exception:
        formatted = code  # formatting is cosmetic, never fail on it
    if len(_format_cache) >= _FORMAT_CACHE_SIZE:
        _format_cache.clear()
    _format_cache[key] = formatted
    return formatted
