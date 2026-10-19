"""Graph -> addon files. Pure: reads bpy data, writes nothing.

    compile_addon(dev=True) -> {"__init__.py": "...", "<tree>.py": "...", ...}

Each tree becomes one module of the add-on package; `__init__.py` imports
them and registers their classes (core/package.py). Root nodes (operators, panels, events, ...) are
emitted first; everything else is emitted when a flow reaches it or when a
value it outputs is used. Nodes write through core/context.NodeContext.
Scripts (core/scripts.py) become modules of their own, unchanged. Trees and
scripts in folders are modules of packages (core/folders.py).
"""

import hashlib
import re
import sys
import textwrap

import bpy

from ..lib import python_format
from ..lib.code_format import sort_imports
from ..lib.logger import log
from ..lib.sockets import to_socket
from ..lib.trees import scripting_node_trees, sn_nodes
from . import errors, functions, helpers, metadata, naming, package, properties
from . import assets as asset_list
from . import scripts as script_list
from .context import Line, NodeContext, NodeError, Scope

HELPERS_MODULE = "utils"

# relpath -> owner node id per line, of the last live compile (error blame)
line_owners: dict[str, list] = {}
# node id -> its own generated lines, of the last live compile (code preview)
node_lines: dict[str, list[str]] = {}
# permissions the nodes of the last live build need (shown in the sidebar)
used_permissions: set[str] = set()

# module name -> modules of trees it is in an import cycle with, of the last
# compile (compile_tree imports those as modules too)
_cycles: dict[str, set[str]] = {}

_format_cache: dict[str, str] = {}
_FORMAT_CACHE_SIZE = 256


# -----------------------------------------------------------------------------
# Entry points
# -----------------------------------------------------------------------------


def compile_addon(dev=True, pretty=False, settings=None, owners_out=None):
    """All files of the generated addon. Empty if there are no trees.

    `dev`: live addon (True) or export (False). `pretty`: format the code
    like `ruff format` (export; scripts stay as written). `owners_out`: a
    dict that gets {relpath: owner node id per line} (unformatted builds)
    and {(relpath, "values"): [(value node id, expression)]}."""
    trees = scripting_node_trees()
    if not trees:
        return {}
    if settings is None:
        settings = bpy.context.scene.sna.addon
    errors.node_errors.clear()
    errors.property_errors.clear()
    names = naming.build(trees, settings)
    naming.use(names)
    files = {"__init__.py": ""}  # first in the folder listing
    owners, previews, used_helpers, permissions = {}, {}, set(), set()
    scripts, assets = {}, {}
    # the add-on's scripts (errors keyed by script id, like nodes)
    errors.node_errors.update(script_list.add_to_addon(names, scripts))
    # functions before the trees calling them: calls pass what they use
    builders = {
        tree.module_name: ModuleBuilder(tree, dev, names, scripts, assets=assets)
        for tree in functions.callees_first(trees)
    }
    results = {module: builder.build() for module, builder in builders.items()}
    # `from .other import name` both ways fails: trees in a cycle import each
    # other as modules and look names up when the code runs
    _cycles.clear()
    _cycles.update(import_cycles({m: b.uses for m, b in builders.items()}))
    for module, peers in _cycles.items():
        builders[module] = ModuleBuilder(
            builders[module].tree, dev, names, scripts, peers, assets
        )
        results[module] = builders[module].build()
    module_files = {}
    for tree in trees:
        builder = builders[tree.module_name]
        source, line_map = results[tree.module_name]
        used_helpers |= builder.helpers
        permissions |= builder.permissions
        if not source.strip():
            continue  # nothing in it (only Trigger nodes in an export)
        rel = module_files[tree.module_name] = tree.module_file
        for folder in _packages(rel):
            files.setdefault(f"{folder}/__init__.py", "")
        files[rel] = source
        owners[rel] = line_map
        previews.update(_previews(source, line_map))
    source = properties.module_source(names, _independent_of_properties(builders))
    if source is not None:
        files[f"{properties.PROPERTIES_MODULE}.py"] = source
    for rel, (source, owner) in scripts.items():
        for folder in _packages(rel):
            files.setdefault(f"{folder}/__init__.py", "")
        files[rel] = source  # the user's code, as written
        owners[rel] = [owner] * (source.count("\n") + 1)
    files.update(assets)  # icons
    # the add-on's assets (errors keyed by asset id, like nodes)
    shipped = {}
    errors.node_errors.update(asset_list.add_to_addon(shipped))
    files.update(shipped)
    files["blender_manifest.toml"] = metadata.manifest(settings, permissions)
    exported = {name for name in used_helpers if helpers.needs_import(name, dev)}
    if exported:
        files[f"{HELPERS_MODULE}.py"] = helpers.source(exported, dev)
    files["__init__.py"] = package.source(
        _package_modules(files, builders, scripts, module_files),
        metadata.license_header(settings),
        metadata.bl_info(settings) if dev else None,
    )
    if owners_out is not None:
        owners_out.update(owners)
        for module, rel in module_files.items():
            owners_out[(rel, "values")] = builders[module].values
    if pretty:
        for rel, source in files.items():
            if rel.endswith(".py") and rel not in scripts:
                files[rel] = _format(source)
    if dev and not pretty:
        line_owners.clear()
        line_owners.update(owners)
        node_lines.clear()
        node_lines.update(previews)
        used_permissions.clear()
        used_permissions.update(permissions)
    return files


def script_file(package: str, module: str) -> str:
    """File of a script's module in the add-on, e.g. `scripts/tools.py`."""
    return "/".join([*package.split("."), module] if package else [module]) + ".py"


def _packages(rel: str) -> list[str]:
    """Folders of the add-on above file `rel`: "a/b/c.py" -> ["a", "a/b"]."""
    parts = rel.split("/")[:-1]
    return ["/".join(parts[: i + 1]) for i in range(len(parts))]


def _independent_of_properties(builders) -> set[str]:
    """Tree modules that don't import from properties.py, not even through
    other modules: properties.py can import them at the top."""
    line = f"from .{properties.PROPERTIES_MODULE} import "
    dependent = {
        module
        for module, builder in builders.items()
        if any(i.startswith(line) for i in builder.imports)
    }
    changed = True
    while changed:
        changed = False
        for module, builder in builders.items():
            if module not in dependent and builder.uses & dependent:
                dependent.add(module)
                changed = True
    return set(builders) - dependent


def _package_modules(files, builders, scripts, module_files) -> list[package.Module]:
    """The add-on's modules in registration order: scripts, helpers,
    properties, then the trees, the ones others import from first."""
    modules = []
    for rel in sorted(scripts):
        path = rel[: -len(".py")].replace("/", ".")
        source = files[rel]
        modules.append(
            package.Module(
                path.rpartition(".")[2],
                path,
                source,
                registers_itself=package.defines(source, "register"),
            )
        )
    for name in (HELPERS_MODULE, properties.PROPERTIES_MODULE):
        if f"{name}.py" in files:
            modules.append(package.Module(name, name, files[f"{name}.py"]))
    uses = {module: builder.uses for module, builder in builders.items()}
    done = set()

    def visit(module, path=()):
        if module in done or module in path:
            return
        for other in sorted(uses.get(module, ())):
            if other in uses:
                visit(other, (*path, module))
        done.add(module)
        rel = module_files.get(module)
        if rel is not None:
            path = rel[: -len(".py")].replace("/", ".")
            modules.append(package.Module(module, path, files[rel]))

    for module in sorted(uses):
        visit(module)
    return modules


def compile_tree(tree, dev=True, pretty=True) -> str:
    """Python source of one tree module."""
    names = naming.build()
    naming.use(names)
    cycle = _cycles.get(tree.module_name, set())
    source, _ = ModuleBuilder(tree, dev, names, module_imports=cycle).build()
    return _format(source) if pretty else source


def import_cycles(uses: dict[str, set[str]]) -> dict[str, set[str]]:
    """{module: other modules of its cycle} for modules that import each
    other, directly or through others (strongly connected components)."""
    index, low, stack, on_stack, result = {}, {}, [], set(), {}

    def visit(module):
        index[module] = low[module] = len(index)
        stack.append(module)
        on_stack.add(module)
        for other in uses.get(module, ()):
            if other not in index:
                visit(other)
                low[module] = min(low[module], low[other])
            elif other in on_stack:
                low[module] = min(low[module], index[other])
        if low[module] == index[module]:
            component = set()
            while True:
                member = stack.pop()
                on_stack.discard(member)
                component.add(member)
                if member == module:
                    break
            if len(component) > 1:
                for member in component:
                    result[member] = component - {member}

    for module in uses:
        if module not in index:
            visit(module)
    return result


# -----------------------------------------------------------------------------
# Module builder
# -----------------------------------------------------------------------------


class ModuleBuilder:
    """Collects the code of one tree module while its nodes emit."""

    def __init__(self, tree, dev, names, scripts=None, module_imports=(), assets=None):
        self.tree = tree
        # other trees' modules imported as modules (import cycles), and the
        # modules this one imports from
        self.module_imports = set(module_imports)
        self.uses: set[str] = set()
        self.dev = dev
        self.names = names
        # {relpath: (source, owner node id)} of script modules, add-on wide
        self.scripts = scripts if scripts is not None else {}
        # {relpath: bytes} of other files (icons), add-on wide
        self.assets = assets if assets is not None else {}
        self.imports = {"import bpy"}
        self.blocks: list[list[Line]] = []
        self.register: list[Line] = []
        self.unregister: list[Line] = []
        self.helpers: set[str] = set()
        # what the add-on does that Blender asks permission for (manifest)
        self.permissions: set[str] = set()
        self._locals: set[str] = set()
        # (node id, expression) of value nodes, written inside other lines
        self.values: list[tuple[str, str]] = []
        self.module_scope = Scope()
        self._emitted: set[int] = set()

    # -- emission -----------------------------------------------------------

    def build(self):
        limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(limit, 20000))  # long flow chains recurse
        try:
            module_scope = self.module_scope
            for node in sn_nodes(self.tree):
                if hasattr(node, "emit_module"):
                    self._emit(node, module_scope, "root", node.emit_module)
            roots = [
                n
                for n in sn_nodes(self.tree)
                if n.sn_root and (self.dev or not n.sn_dev_only)
            ]
            roots.sort(key=lambda n: n.sn_order)
            for node in roots:
                self._emit(node, module_scope, "root")
            if functions.is_function(self.tree):
                self.add_block(self._group_function(module_scope))
        finally:
            sys.setrecursionlimit(limit)
        return self._assemble()

    def _emit(self, node, scope, mode, emit=None) -> NodeContext | None:
        ctx = NodeContext(self, node, scope, mode)
        self._emitted.add(node.as_pointer())
        try:
            (emit or node.emit)(ctx)
            self.permissions.update(getattr(node, "sn_permissions", ()))
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
        if target.node.bl_idname == functions.GROUP_OUTPUT:
            return self._group_return(target.node, scope)
        ctx = self._emit(target.node, scope, "statement")
        if ctx is not None:
            return ctx.lines()
        # a broken node is left out, what comes after it still runs
        after = next((s for s in target.node.outputs if s.identifier == "next"), None)
        if after is None or not after.enabled:
            return []
        return self.compile_flow(after, scope)

    def evaluate(self, node, key, scope) -> str:
        """Expression of output `key` of a value node."""
        ctx = self._emit(node, scope, "value")
        if ctx is None:
            return "None"
        expression = ctx.outputs.get(key, "None")
        self.values.append((node.id, expression))
        return expression

    def add_block(self, lines):
        if any(line.text for line in lines):
            self.blocks.append(lines)

    # -- module services ------------------------------------------------------

    def unique_name(self, base, scope=None):
        """A local name not used in this module (nor as module level name or
        parameter in `scope`)."""
        taken = self._locals | self.names.used["symbol"]
        while scope is not None:
            taken |= scope.names
            scope = scope.parent
        name = naming.unique(base, taken)
        self._locals.add(name)
        return name

    def use_helper(self, name):
        if name not in helpers.HELPERS:
            raise NodeError(f"Unknown helper '{name}'")
        self.helpers.add(name)
        for required in helpers.HELPERS[name].requires:
            self.use_helper(required)
        if helpers.needs_import(name, self.dev):
            self.imports.add(f"from . import {HELPERS_MODULE}")
            return f"{HELPERS_MODULE}.{helpers.call_name(name, self.dev)}"
        return helpers.call_name(name, self.dev)

    def add_script(self, module, alias, source, owner, folder=""):
        """Add `source` as `<folder>/<module>.py` (once for the add-on) and
        import it into this module as `alias`."""
        package = naming.package(folder)
        self.scripts.setdefault(script_file(package, module), (source, owner))
        line = f"from .{package} import {module}"
        self.imports.add(line if alias == module else f"{line} as {alias}")
        return alias

    def add_asset(self, rel, data: bytes) -> str:
        """Add the file `rel` (e.g. "icons/logo.png") to the add-on. A
        different file of the same name gets a suffix; returns the path used."""
        stem, dot, ext = rel.rpartition(".")
        if not dot:
            stem, ext = rel, ""
        candidate, i = rel, 1
        while self.assets.get(candidate, data) != data:
            i += 1
            candidate = f"{stem}_{i}{dot}{ext}"
        self.assets[candidate] = data
        return candidate

    def import_symbol(self, owner, name):
        """`name` from the module of `owner`'s tree: imported by name, or used
        through the module if the two trees import each other."""
        tree = owner if hasattr(owner, "nodes") else owner.id_data
        if tree == self.tree:
            return name
        module = tree.module_name
        self.uses.add(module)
        path = tree.module_path
        if module not in self.module_imports:
            self.imports.add(f"from .{path} import {name}")
            return name
        alias = f"_{module}"
        package, _, module_name = path.rpartition(".")
        self.imports.add(f"from .{package} import {module_name} as {alias}")
        return f"{alias}.{name}"

    # -- functions (node groups) ---------------------------------------------

    def _group_function(self, module_scope) -> list[Line]:
        """A tree with a group interface compiles to `def <function>(params,
        *, context, ...)` with the names of the caller's scope it uses (self,
        context, layout, event), see core/functions.py."""
        tree = self.tree
        params = functions.parameters(tree)
        names = [name for _, name in params]
        implicit = list(functions.IMPLICIT)
        values = {}
        for node in functions.group_inputs(tree):
            for item, name in params:
                values[(node.as_pointer(), item.identifier)] = name
        scope = Scope(module_scope, "layout", values, frozenset(names + implicit))

        body = []
        flow = functions.flow_input(tree)
        if flow is not None:
            for node in functions.group_inputs(tree):
                socket = next(
                    (s for s in node.outputs if s.identifier == flow.identifier), None
                )
                if socket is not None and socket.is_linked:
                    body = self.compile_flow(socket, scope)
                    break
        output = functions.active_output(tree)
        if output is not None and output.as_pointer() not in self._emitted:
            ret = self._group_return(output, scope)
            body += ret
        while body and not body[-1].text:
            body.pop()
        if body and body[-1].indent == 0 and body[-1].text == "return":
            body.pop()  # a bare return at the end does nothing

        text = "\n".join(line.text for line in body)
        used = [n for n in implicit if re.search(rf"(?<![.\w]){n}\b", text)]
        functions.implicit_used[tree.name] = tuple(used)
        signature = ", ".join(names + (["*", *used] if used else []))
        lines = [Line(0, f"def {tree.function_name}({signature}):", None)]
        lines += [Line(4 + line.indent, line.text, line.owner) for line in body]
        return lines

    def _group_return(self, node, scope) -> list[Line]:
        """`return ...` with the values connected to a Group Output."""
        self._emitted.add(node.as_pointer())
        ctx = NodeContext(self, _InterfaceNode(node), scope, "statement")
        values = []
        for item in functions.returns(self.tree):
            try:
                values.append(ctx.input(item.identifier))
            except NodeError as exc:
                log("WARNING", f"'{self.tree.name}' return value '{item.name}': {exc}")
                values.append("None")
        return [Line(0, " ".join(["return", ", ".join(values)]).strip(), None)]

    # -- assembly -------------------------------------------------------------

    def _assemble(self):
        blocks = list(self.blocks)
        for name, body in (
            ("register", self.register),
            ("unregister", self.unregister),
        ):
            if not any(line.text for line in body):
                continue
            function = [Line(0, f"def {name}():", None)]
            function += [Line(4 + line.indent, line.text, line.owner) for line in body]
            blocks.append(function)
        package = naming.package(self.tree.folder)
        if package:
            blocks = [[_in_subpackage(line) for line in block] for block in blocks]
        code = "\n".join(line.text for block in blocks for line in block)
        if package and re.search(rf"\b{BASE_PACKAGE}\b", code):
            self.imports.add(f"from . import __package__ as {BASE_PACKAGE}")
        # nodes that failed may have added imports their code never used
        imports = {kept for line in self.imports if (kept := _used_import(line, code))}
        # imports are written relative to the add-on's folder
        imports = {naming.relative_import(line, package) for line in imports}
        if imports:
            blocks.insert(0, [Line(0, line, None) for line in sort_imports(imports)])

        lines: list[Line] = []
        for i, block in enumerate(blocks):
            if i == 1 and imports and not block[0].text.startswith(_DEFINITIONS):
                lines.append(Line(0, "", None))  # isort: one after imports
            elif i:
                lines += [Line(0, "", None), Line(0, "", None)]
            lines += block
        lines = _finalize(lines)
        source = "\n".join(" " * l.indent + l.text if l.text else "" for l in lines)
        # nodes put parentheses around the values they combine
        source = python_format.remove_redundant_parens(source + "\n")
        return source, [l.owner for l in lines]


_DEFINITIONS = ("def ", "class ", "@", "async def ")

# `__package__` of the add-on in modules of its folders (Blender's idiom for
# sub-modules of extensions)
BASE_PACKAGE = "base_package"


def _in_subpackage(line: Line) -> Line:
    """`__package__` (the add-on) in a module of a folder."""
    if "__package__" not in line.text:
        return line
    text = re.sub(r"\b__package__\b", BASE_PACKAGE, line.text)
    return line._replace(text=text)


def _used_import(line: str, code: str) -> str | None:
    """`line` with only the names `code` uses, None if it uses none."""

    def used(name):
        return re.search(rf"\b{re.escape(name)}\b", code) is not None

    if not line.startswith("from "):
        name = line.split(" as ")[-1].split()[-1].split(".")[0]
        return line if used(name) else None
    head, names = line.split(" import ", 1)
    kept = [n.strip() for n in names.split(",") if used(n.split(" as ")[-1].strip())]
    return f"{head} import {', '.join(kept)}" if kept else None


class _InterfaceNode:
    """Group Input / Output seen as a node NodeContext can read inputs of."""

    id = None

    def __init__(self, node):
        self._node = node

    def __getattr__(self, name):
        return getattr(self._node, name)

    def socket(self, key, output=False):
        sockets = self._node.outputs if output else self._node.inputs
        return next((s for s in sockets if s.identifier == key), None)


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
    return _blank_lines(final)


def _blank_lines(lines: list[Line]) -> list[Line]:
    """At most two blank lines in a row at the top level and one inside
    blocks, none at the start of a block (empty bodies of templates)."""
    if any('"""' in line.text or "'''" in line.text for line in lines):
        return lines  # blank lines may be part of a string
    result: list[Line] = []
    for i, line in enumerate(lines):
        if line.text:
            result.append(line)
            continue
        following = next((l for l in lines[i + 1 :] if l.text), None)
        previous = next((l for l in reversed(result) if l.text), None)
        if following is None or previous is None:
            continue
        if previous.text.rstrip().endswith(":") and following.indent > previous.indent:
            continue
        blanks = 0
        for earlier in reversed(result):
            if earlier.text:
                break
            blanks += 1
        if blanks < (2 if following.indent == 0 else 1):
            result.append(line)
    return result


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


def _format(code: str) -> str:
    key = hashlib.sha1(code.encode()).hexdigest()
    cached = _format_cache.get(key)
    if cached is not None:
        return cached
    formatted = python_format.format_source(code)
    if len(_format_cache) >= _FORMAT_CACHE_SIZE:
        _format_cache.clear()
    _format_cache[key] = formatted
    return formatted
