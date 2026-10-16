"""The add-on as a whole: settings, problems, code, export, running it."""

import contextlib
import io
import os
import traceback

import bpy

from ...core import compiler, errors, export_check, properties, runtime
from ...core.ops import export
from ...lib.trees import node_by_id, scripting_node_trees
from . import tool
from ._common import ToolError, set_rna, tree_info
from .blender import override

# add-on settings set_addon may change, with what they mean
SETTINGS = {
    "addon_name": "Name of the add-on (also its module name and class prefix)",
    "tagline": "One line saying what it does",
    "author": "Maintainer",
    "email": "Maintainer's email",
    "version": "[major, minor, patch]",
    "website": "URL",
    "location": "Where to find it, e.g. 'View3D > Sidebar'",
    "tags": "List of extension platform tags",
    "copyright": "'2026 Jane Doe'",
    "blender_version_min": "[major, minor, patch]",
    "permission_files": "Ask for file access (nodes that need it turn it on)",
    "files_reason": "Why, shown to the user",
    "permission_network": "Ask for network access",
    "network_reason": "Why",
    "permission_clipboard": "Ask for clipboard access",
    "clipboard_reason": "Why",
    "enabled": "Build and load the add-on while working",
    "persist_addon": "Keep the add-on loaded in other files",
}


def addon():
    return bpy.context.scene.sna.addon


def _metadata(settings):
    result = {}
    for name in SETTINGS:
        if name in ("addon_name", "enabled"):
            continue
        prop = settings.bl_rna.properties.get(name)
        if prop is None:
            continue
        val = getattr(settings, name)
        if isinstance(val, set):
            val = sorted(val)
        elif not isinstance(val, (str, bool, int, float)):
            val = list(val)
        if val not in ("", False, []):
            result[name] = val
    return result


def property_lists():
    """[{owner, properties}] of every property list."""
    result = []
    for kind, owner, items in properties.lists():
        if kind == "ADDON":
            label = "addon"
        elif kind == "GROUP":
            label = f"group:{owner.name}"
        else:
            label = owner.id
        entries = []
        for prop in items:
            entry = {"name": prop.name, "type": prop.property_type, "id": prop.id}
            if kind == "ADDON" and prop.property_type != "GROUP":
                entry["on"] = prop.attach_to
            if prop.uses_group:
                group = properties.find_group(prop.group_id)
                entry["group"] = group.name if group else None
            entries.append(entry)
        info = {"owner": label, "properties": entries}
        if kind == "NODE":
            info["node"] = f"{owner.id_data.name}/{owner.name}"
        result.append(info)
    return result


@tool(
    "get_addon",
    """Overview of the add-on built from this file: name, module, whether
    it's loaded, metadata, node trees, property lists and how many problems
    there are. Start here.""",
)
def get_addon():
    settings = addon()
    module = settings.module_name
    problems = get_problems(check_export=False)
    return {
        "name": settings.addon_name,
        "module": module,
        "enabled": settings.enabled,
        "loaded": runtime.is_loaded(module),
        "folder": runtime.folder(module),
        "metadata": _metadata(settings),
        "trees": [tree_info(t) for t in scripting_node_trees()],
        "property_lists": property_lists(),
        "problems": {
            "build_error": bool(problems.get("build_error")),
            "nodes": len(problems.get("nodes", [])),
            "properties": len(problems.get("properties", [])),
        },
    }


@tool(
    "set_addon",
    "Change add-on settings and metadata. Settings: "
    + "; ".join(f"{k}: {v}" for k, v in SETTINGS.items()),
    {"settings": {"type": "object", "description": "{setting: value}"}},
    required=["settings"],
    writes=True,
)
def set_addon(settings):
    target = addon()
    for name, raw in settings.items():
        if name not in SETTINGS:
            raise ToolError(f"Unknown setting {name!r}. Settings: {list(SETTINGS)}")
        set_rna(target, name, raw)
    return {"module": target.module_name, "metadata": _metadata(target)}


@tool(
    "get_problems",
    """Everything that's wrong: nodes with errors (missing setup, code that
    failed when it ran), property definitions with errors, the error of the
    last build if the add-on failed to load, and (check_export) what the
    extensions platform's reviewers would ask to change.""",
    {
        "check_export": {
            "type": "boolean",
            "description": "Also check the export (default true)",
        }
    },
)
def get_problems(check_export=True):
    result = {}
    if errors.addon_error:
        result["build_error"] = errors.addon_error[-4000:]
    nodes = []
    seen = set()
    for source in (errors.node_errors, errors.load_errors, errors.runtime_errors):
        for node_id, message in source.items():
            node = node_by_id(node_id)
            if node is None or node_id in seen:
                continue
            seen.add(node_id)
            nodes.append(
                {
                    "node": node_id,
                    "name": node.name,
                    "tree": node.id_data.name,
                    "error": message,
                }
            )
    if nodes:
        result["nodes"] = nodes
    props = []
    for prop_id, message in errors.property_errors.items():
        found = properties.find(prop_id)
        name = found.prop.name if found else prop_id
        props.append({"property": prop_id, "name": name, "error": message})
    if props:
        result["properties"] = props
    if check_export:
        issues = export_check.run()
        if issues:
            result["export_check"] = [
                {
                    "severity": i.severity,
                    "message": i.message,
                    **({"node": i.node_id} if i.node_id else {}),
                }
                for i in issues
            ]
    return result


@tool(
    "get_code",
    """The generated Python: of one tree, or all files of the add-on. The
    live build (default) is what runs while working; export=true gives the
    files as exported (formatted, without Trigger nodes).""",
    {
        "tree": {"type": "string", "description": "Only this tree's module"},
        "export": {"type": "boolean"},
    },
)
def get_code(tree="", export=False):
    if export:
        files = export.build_files()
    else:
        files = compiler.compile_addon(dev=True)
    files = {k: v for k, v in files.items() if isinstance(v, str)}
    if tree:
        from ._common import find_tree

        rel = f"{find_tree(tree).module_name}.py"
        if rel not in files:
            return {"files": {}, "note": "The tree writes no code (yet)"}
        return {"files": {rel: files[rel]}}
    return {"files": files}


@tool(
    "export_addon",
    """Export the add-on as an installable extension zip and check it
    against the extensions platform's guidelines.""",
    {"filepath": {"type": "string", "description": "Path of the .zip"}},
    required=["filepath"],
)
def export_addon(filepath):
    path = os.path.abspath(bpy.path.abspath(filepath))
    if not path.endswith(".zip"):
        path += ".zip"
    files = export.build_files()
    if not files:
        raise ToolError("Nothing to export: add a node tree first")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    export.write_zip(path, files)
    issues = export_check.run()
    return {
        "path": path,
        "files": sorted(files),
        "issues": [f"{i.severity}: {i.message}" for i in issues],
    }


@tool(
    "run_operator",
    """Run an operator (e.g. one of the add-on, 'my_addon.do_thing') and get
    its result and what it printed. Properties as {name: value}. invoke=true
    runs it as a click would (dialogs show; use for the user to see).""",
    {
        "idname": {"type": "string"},
        "properties": {"type": "object"},
        "invoke": {"type": "boolean"},
        "area": {
            "type": "string",
            "description": "Editor it runs in, e.g. VIEW_3D (some need one)",
        },
    },
    required=["idname"],
    writes=True,
)
def run_operator(idname, properties=None, invoke=False, area=""):
    namespace, _, name = idname.partition(".")
    operator = getattr(getattr(bpy.ops, namespace, None), name, None)
    if not name or operator is None:
        raise ToolError(f"No operator {idname!r}")
    out = io.StringIO()
    result = {}
    try:
        with contextlib.redirect_stdout(out), override(area or None):
            if not operator.poll():
                raise ToolError(f"{idname} can't run now (its poll() is False)")
            context = "INVOKE_DEFAULT" if invoke else "EXEC_DEFAULT"
            result["result"] = sorted(operator(context, **(properties or {})))
    except ToolError:
        raise
    except (RuntimeError, TypeError) as exc:
        result["error"] = str(exc)
    except Exception:  # noqa: BLE001 - the add-on's own errors
        result["error"] = traceback.format_exc(limit=-6)
    if out.getvalue():
        result["output"] = out.getvalue()[-10000:]
    return result
