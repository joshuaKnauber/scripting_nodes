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
    for tree in trees:
        files[f"addon/{tree.module_name}.py"] = compile_tree(tree, pretty)
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
    source = _assemble_tree(tree)
    return _format(source) if pretty else source


def _assemble_tree(tree) -> str:
    nodes = sn_nodes(tree)

    import_lines = {"import bpy"}
    for node in nodes:
        for line in normalize_indents(node.code_imports).split("\n"):
            if line.strip():
                import_lines.add(line.strip())
    parts = ["\n".join(sorted(import_lines)), ""]

    for node in nodes:
        if node.code_global:
            parts.append(normalize_indents(node.code_global))

    # PropertyGroups first: Operator/Preferences/Panel class bodies may
    # reference them (PointerProperty(type=PG)) at class-definition time.
    root_nodes = [n for n in nodes if "ROOT_NODE" in n.sn_options]
    root_nodes.sort(key=lambda n: 0 if n.bl_idname == "SNA_Node_PropertyGroup" else 1)
    for node in root_nodes:
        if node.code_module:
            parts.append(normalize_indents(node.code_module))

    if tree.is_group:
        parts.append(_group_function(tree))

    register = [normalize_indents(n.code_register) for n in nodes if n.code_register]
    unregister = [
        normalize_indents(n.code_unregister) for n in nodes if n.code_unregister
    ]
    parts.append(_function("register", register))
    parts.append(_function("unregister", unregister))
    return "\n\n".join(parts) + "\n"


def _function(name, bodies):
    lines = [line for body in bodies for line in body.split("\n")]
    if not lines:
        lines = ["pass"]
    return f"def {name}():\n" + "\n".join(f"    {line}" for line in lines)


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
