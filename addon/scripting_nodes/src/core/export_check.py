"""Checks an export against the moderation guidelines of
extensions.blender.org: what reviewers reject or ask to change, found in the
generated code and blamed on the node that wrote it.

    run() -> [Issue, ...]

Errors are things the platform rejects (changing `sys`, `bl_ext`, writing
into the add-on's folder, network access without the permission), warnings
are things reviewers flag (`bpy.data` instead of the scene's data, data-blocks
assumed by name, missing metadata).
"""

import ast
import tomllib
from typing import NamedTuple

import bpy

from . import compiler, metadata

GUIDELINES = (
    "https://developer.blender.org/docs/features/extensions/moderation/guidelines/"
)


class Issue(NamedTuple):
    severity: str  # "ERROR" or "WARNING"
    message: str
    node_id: str | None = None
    file: str = ""
    line: int = 0


# issues of the last check (shown in the sidebar)
last: list[Issue] = []
checked = False

# attributes of bpy.data that aren't collections of data-blocks
_NOT_DATA = {"filepath", "is_dirty", "is_saved", "use_autopack", "version"}
_NETWORK = {"urllib", "requests", "http", "socket", "ftplib", "smtplib", "aiohttp"}
_FILE_CALLS = {
    "open",
    "makedirs",
    "mkdir",
    "remove",
    "unlink",
    "rename",
    "rmtree",
    "copy",
    "copyfile",
    "copytree",
    "move",
    "write_text",
    "write_bytes",
}
_WRITE_CALLS = _FILE_CALLS - {"open"}


def run(settings=None) -> list[Issue]:
    """Check the add-on of the current file as it would be exported."""
    global last, checked
    settings = settings or bpy.context.scene.sna.addon
    owners: dict = {}
    files = compiler.compile_addon(dev=False, settings=settings, owners_out=owners)
    issues = check(files, owners, settings)
    last, checked = issues, True
    return issues


def check(files, owners, settings) -> list[Issue]:
    issues = []
    try:
        manifest = tomllib.loads(files.get("blender_manifest.toml", ""))
    except tomllib.TOMLDecodeError:
        manifest = {}
    permissions = set(manifest.get("permissions", {}))
    for rel, source in sorted(files.items()):
        if not rel.endswith(".py") or not isinstance(source, str):
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue  # shown as a build error
        lines = owners.get(rel, [])
        values = owners.get((rel, "values"), [])
        for severity, message, node in _check_module(tree, permissions):
            line = getattr(node, "lineno", 0)
            owner = _value_node(ast.get_source_segment(source, node), values)
            if owner is None and 0 < line <= len(lines):
                owner = lines[line - 1]
            issues.append(Issue(severity, message, owner, rel, line))
    issues += _check_metadata(settings)
    # one entry per node and message
    seen, unique = set(), []
    for issue in issues:
        key = (issue.message, issue.node_id or (issue.file, issue.line))
        if key not in seen:
            seen.add(key)
            unique.append(issue)
    unique.sort(key=lambda i: (i.severity != "ERROR", i.file, i.line))
    return unique


def _value_node(segment, values):
    """The value node whose expression contains `segment` (the smallest),
    None if it's written by the line's own node."""
    if not segment:
        return None
    containing = [(len(expr), node) for node, expr in values if segment in expr]
    return min(containing)[1] if containing else None


def _check_metadata(settings):
    found = []
    if not settings.author.strip():
        found.append(Issue("WARNING", "Set an author (Metadata)"))
    if not settings.tagline.strip() or settings.tagline == metadata.DEFAULT_TAGLINE:
        found.append(Issue("WARNING", "Write a tagline saying what it does (Metadata)"))
    for problem in metadata.problems(settings):
        found.append(Issue("WARNING", problem))
    return found


# -- code ---------------------------------------------------------------------------


def _dotted(node) -> str:
    """`a.b.c` of an attribute chain, "" for anything else."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return ""


def _data_collections():
    return {
        prop.identifier
        for prop in bpy.types.BlendData.bl_rna.properties
        if prop.type == "COLLECTION"
    }


def _called(call) -> str:
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _uses_file_dunder(node) -> bool:
    return any(isinstance(n, ast.Name) and n.id == "__file__" for n in ast.walk(node))


def _opens_for_writing(call) -> bool:
    mode = call.args[1] if len(call.args) > 1 else None
    for keyword in call.keywords:
        if keyword.arg == "mode":
            mode = keyword.value
    return (
        isinstance(mode, ast.Constant)
        and isinstance(mode.value, str)
        and any(c in mode.value for c in "wax+")
    )


def _check_module(tree, permissions):
    """(severity, message, syntax node) of the guideline issues in one
    module."""
    collections = _data_collections()
    text_uses = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)} | {
        n.id for n in ast.walk(tree) if isinstance(n, ast.Name)
    }

    for node in ast.walk(tree):
        # bpy.data.objects, bpy.data.objects["Cube"]
        if isinstance(node, ast.Attribute):
            dotted = _dotted(node)
            if dotted.startswith("bpy.data.") and dotted.count(".") == 2:
                if node.attr in collections:
                    yield (
                        "WARNING",
                        f"Uses all of bpy.data.{node.attr}: work on the scene's "
                        "data instead (Context: scene.objects, selected_objects)",
                        node,
                    )
            if node.attr == "clipboard" and "clipboard" not in permissions:
                yield "ERROR", "Uses the clipboard: turn on its permission", node
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            value = node.slice.value
            owner = node.value
            if (
                isinstance(value, str)
                and isinstance(owner, ast.Attribute)
                and owner.attr in collections
            ):
                yield (
                    "WARNING",
                    f"Expects a data-block named '{value}': it may not exist in "
                    "the user's file",
                    node,
                )
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Attribute)
            and node.value.attr == "addons"
            and isinstance(node.slice, ast.Name)
            and node.slice.id == "__name__"
        ):
            yield "ERROR", "Use __package__, not __name__, for the add-on", node

        # sys is read-only
        if isinstance(node, (ast.Assign, ast.AugAssign, ast.Delete)):
            targets = node.targets if hasattr(node, "targets") else [node.target]
            for target in targets:
                root = target.value if isinstance(target, ast.Subscript) else target
                if _dotted(root).startswith("sys."):
                    yield "ERROR", "Changes the sys module (it's read-only)", node
        if isinstance(node, ast.Call):
            called = _called(node)
            dotted = _dotted(node.func)
            if dotted.startswith(("sys.path.", "sys.modules.")) and called in (
                "append",
                "insert",
                "extend",
                "remove",
                "pop",
                "update",
                "setdefault",
            ):
                yield "ERROR", "Changes the sys module (it's read-only)", node

            # files
            writes = called in _WRITE_CALLS or (
                called == "open" and _opens_for_writing(node)
            )
            if writes and any(_uses_file_dunder(arg) for arg in node.args):
                yield (
                    "ERROR",
                    "Writes into the add-on's folder, which updates replace: use "
                    "bpy.utils.extension_path_user(__package__, create=True)",
                    node,
                )
            if called in _FILE_CALLS and "files" not in permissions:
                yield (
                    "ERROR",
                    "Reads or writes files: turn on the Files permission",
                    node,
                )

        # strings
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "bl_ext" in node.value or node.value in ("user_default", "blender_org"):
                yield (
                    "ERROR",
                    "Refers to an extension repository by name; use __package__",
                    node,
                )

        # network
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = (
                [a.name for a in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
            )
            if any(m.split(".")[0] in _NETWORK for m in modules):
                if "network" not in permissions:
                    yield (
                        "ERROR",
                        "Connects to the internet: turn on the Network permission",
                        node,
                    )
                if "online_access" not in text_uses:
                    yield (
                        "ERROR",
                        "Connects to the internet without checking "
                        "bpy.app.online_access first",
                        node,
                    )

    # the add-on keyconfig is None in background mode
    for function in ast.walk(tree):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        uses = [
            n
            for n in ast.walk(function)
            if isinstance(n, ast.Attribute)
            and n.attr == "addon"
            and _dotted(n).endswith("keyconfigs.addon")
        ]
        checks_none = any(
            isinstance(n, ast.Compare)
            and any(
                isinstance(c, ast.Constant) and c.value is None for c in n.comparators
            )
            for n in ast.walk(function)
        ) or any(
            isinstance(n, ast.If) and isinstance(n.test, (ast.Name, ast.UnaryOp))
            for n in ast.walk(function)
        )
        if uses and not checks_none:
            yield (
                "WARNING",
                "Check that window_manager.keyconfigs.addon isn't None "
                "(it is in background mode)",
                uses[0],
            )
