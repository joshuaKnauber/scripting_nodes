"""Node code -> addon files. Pure: reads bpy data, never writes anything.

    compile_addon() -> {"__init__.py": "...", "addon/tree_x.py": "...", ...}

Every node already holds its generated code (set by the scheduler's
regenerate pass); this module only assembles it into modules and fills the
package templates. The same function feeds the live addon and the export.
"""

import hashlib
import os

import bpy

from ..lib.code_format import normalize_indents
from ..lib.trees import scripting_node_trees, sn_nodes

TEMPLATES = os.path.join(os.path.dirname(__file__), "templates")

# relpath -> line owners of the last live (unformatted) compile, used to show
# load errors on the node that produced the failing line
line_owners: dict[str, list] = {}

# raw source hash -> formatted source. autopep8 is by far the slowest step of
# compiling, and most flushes only change one tree.
_format_cache: dict[str, str] = {}
_FORMAT_CACHE_SIZE = 256


def compile_addon(settings=None, pretty=False) -> dict[str, str]:
    """All files of the generated addon. Empty dict if there is no addon.

    `pretty` runs autopep8 over the tree modules. It's the slowest part of
    compiling, so the live addon skips it; export and code views use it.
    """
    trees = scripting_node_trees()
    if not trees:
        return {}
    if settings is None:
        settings = bpy.context.scene.sna.addon
    values = {
        "$ADDON_NAME": settings.addon_name,
        "$MODULE_NAME": settings.module_name,
    }
    files = {
        "__init__.py": _render("init.txt", values),
        "auto_load.py": _render("auto_load.txt", values),
        "blender_manifest.toml": _render("blender_manifest.txt", values),
        "addon/__init__.py": "",
    }
    owners = {}
    for tree in trees:
        rel = f"addon/{tree.module_name}.py"
        source, owners[rel] = assemble_tree(tree)
        files[rel] = _format(source) if pretty else source
    if not pretty:
        line_owners.clear()
        line_owners.update(owners)
    return files


def _render(template, values):
    with open(os.path.join(TEMPLATES, template)) as f:
        text = f.read()
    for key, value in values.items():
        text = text.replace(key, value)
    return text


# ---------------------------------------------------------------------------
# Tree modules
# ---------------------------------------------------------------------------


def compile_tree(tree, pretty=True) -> str:
    """Python source of one tree module."""
    source, _ = assemble_tree(tree)
    return _format(source) if pretty else source


def assemble_tree(tree):
    """(source, line_owners) of one tree module, unformatted.

    `line_owners[i]` is the id of the node that produced line i + 1 (or None),
    so errors pointing at a line can be shown on the node. Flow code nested
    inside another node's block is attributed to that outer node.
    """
    nodes = sn_nodes(tree)
    blocks = []  # each block: list of (line, owner node id or None)

    def block(text, owner=None):
        return [(line, owner) for line in text.split("\n")]

    import_lines = {"import bpy"}
    for node in nodes:
        for line in normalize_indents(node.code_imports).split("\n"):
            if line.strip():
                import_lines.add(line.strip())
    blocks.append(block("\n".join(sorted(import_lines))))

    for node in nodes:
        if node.code_global:
            blocks.append(block(normalize_indents(node.code_global), node.id))

    # PropertyGroups first: Operator/Preferences/Panel class bodies may
    # reference them (PointerProperty(type=PG)) at class-definition time.
    root_nodes = [n for n in nodes if "ROOT_NODE" in n.sn_options]
    root_nodes.sort(key=lambda n: 0 if n.bl_idname == "SNA_Node_PropertyGroup" else 1)
    for node in root_nodes:
        if node.code_module:
            blocks.append(block(normalize_indents(node.code_module), node.id))

    if tree.is_group:
        blocks.append(block(_group_function(tree)))

    for name, field in (
        ("register", "code_register"),
        ("unregister", "code_unregister"),
    ):
        function = [(f"def {name}():", None)]
        for node in nodes:
            if getattr(node, field):
                body = normalize_indents(getattr(node, field))
                function += [("    " + line, node.id) for line in body.split("\n")]
        if len(function) == 1:
            function.append(("    pass", None))
        blocks.append(function)

    lines, owners = [], []
    for i, current in enumerate(blocks):
        if i:
            lines += ["", ""]
            owners += [None, None]
        for line, owner in current:
            lines.append(line)
            owners.append(owner)
    return "\n".join(lines) + "\n", owners


# Names from the caller's method scope that group functions pull in so emitted
# bare references (self.layout, context.scene, ...) resolve. Callers pass
# `_locals=locals()`.
_GROUP_CALLER_LOCALS = ("self", "context", "event", "dummy")


def _group_function(tree):
    """`def <module_name>(params, _locals=None): body; return ...`"""
    group_input = group_output = None
    for node in sn_nodes(tree):
        if node.bl_idname == "SNA_Node_GroupInput" and group_input is None:
            group_input = node
        elif node.bl_idname == "SNA_Node_GroupOutput" and group_output is None:
            group_output = node

    params = [item["name"] for item in group_input.get_items()] if group_input else []
    params.append("_locals=None")

    if group_input and len(group_input.outputs) > 0:
        body = group_input.outputs[0].eval("pass")
    else:
        body = "pass"

    return_line = None
    if group_output:
        reserved = getattr(group_output, "reserved_count", 1)
        returns = []
        for i, _item in enumerate(group_output.get_items()):
            index = i + reserved
            if index < len(group_output.inputs):
                returns.append(group_output.inputs[index].eval("None"))
        if len(returns) == 1:
            return_line = f"return {returns[0]}"
        elif returns:
            return_line = "return (" + ", ".join(returns) + ")"

    lines = [f"def {tree.module_name}({', '.join(params)}):"]
    lines.append("    _locals = _locals or {}")
    for name in _GROUP_CALLER_LOCALS:
        lines.append(f"    {name} = _locals.get({name!r})")
    for line in (normalize_indents(body) or "pass").split("\n"):
        lines.append(("    " + line) if line.strip() else "")
    if return_line:
        lines.append("    " + return_line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


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
