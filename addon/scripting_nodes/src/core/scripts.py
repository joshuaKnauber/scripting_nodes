"""Python from a Text block or a file: the add-on's scripts (Addon Data ›
Scripts, `scene.sna.addon.scripts`) and Inline Script nodes.

Every script of the list is part of the add-on as `<folder>/<name>.py`
(core/folders.py), unchanged: its classes are registered, its `register()` / `unregister()`
called. Script Function nodes pick one by id and call its functions; their
signatures declare the sockets (core/script_signatures.py).
"""

import os

import bpy

from ..lib.trees import scripting_node_trees, sn_nodes
from . import naming, scheduler, script_signatures
from .context import NodeError


class ScriptSource:
    """Reading the source of an owner with `source_type`, `text_block` and
    `filepath` (a list script or an Inline Script node)."""

    def source_name(self):
        """(owner, base name) of the script, or None. Owners using the same
        text or file share its module."""
        if self.source_type == "INTERNAL":
            if self.text_block is None:
                return None
            name = self.text_block.name
            return "text:" + name, os.path.splitext(name)[0]
        if not self.filepath:
            return None
        path = os.path.normpath(bpy.path.abspath(self.filepath))
        return "file:" + path, os.path.splitext(os.path.basename(path))[0]

    def source_fingerprint(self):
        """Changes whenever the source changes (watched, editing a text or
        saving a file triggers no update)."""
        if self.source_type == "INTERNAL":
            return hash(self.text_block.as_string()) if self.text_block else None
        path = bpy.path.abspath(self.filepath) if self.filepath else ""
        try:
            stat = os.stat(path)
            return (path, stat.st_mtime_ns, stat.st_size)
        except OSError:
            return (path, None)

    def script_source(self):
        if self.source_type == "INTERNAL":
            if self.text_block is None:
                raise NodeError("Pick a text block")
            return self.text_block.as_string()
        if not self.filepath:
            raise NodeError("Pick a Python file")
        path = bpy.path.abspath(self.filepath)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError as exc:
            raise NodeError(f"Can't read {path}: {exc.strerror or exc}")

    def script(self):
        """What the script defines (script_signatures.Script)."""
        try:
            return script_signatures.read(self.script_source())
        except script_signatures.ScriptError as exc:
            raise NodeError(f"Script: {exc}")

    def script_functions(self):
        """Names of the script's functions, [] if it can't be read."""
        if self.source_name() is None:
            return []
        try:
            return list(self.script().functions)
        except NodeError:
            return []

    def source_label(self):
        """The text's name or the file's name."""
        if self.source_type == "INTERNAL":
            return self.text_block.name if self.text_block else ""
        return os.path.basename(self.filepath) if self.filepath else ""


# -- the list ---------------------------------------------------------------------


def scripts():
    scene = bpy.context.scene
    return scene.sna.addon.scripts if scene is not None else []


def find(script_id):
    if not script_id:
        return None
    return next((s for s in scripts() if s.id == script_id), None)


def label(script) -> str:
    return script.source_label() or "(no script)"


def choices():
    """(label, script) of the list's scripts, labels unique."""
    result, seen = [], set()
    for script in scripts():
        result.append((naming.unique(label(script), seen), script))
    return result


def names(script) -> list:
    """Names of the script's module, see naming.Script."""
    source = script.source_name()
    if source is None:
        return []
    owner, base = source
    return [
        naming.Script("module", base, owner),
        naming.Symbol("alias", naming.snake(base, "script"), owner=owner),
    ]


def callers(script):
    """Script Function nodes calling a function of `script`."""
    return [
        node
        for tree in scripting_node_trees()
        for node in sn_nodes(tree)
        if node.bl_idname == "SNA_Node_ScriptFunction" and node.script_id == script.id
    ]


def add_to_addon(names_registry, files):
    """Add the list's scripts to `files` ({rel: (source, owner id)}).
    Returns {script id: error} of those that can't be added."""
    from .compiler import script_file

    problems = {}
    for script in scripts():
        if script.source_name() is None:
            continue
        try:
            script.script()  # parses
            source = script.script_source()
        except NodeError as exc:
            problems[script.id] = str(exc)
            continue
        module = names_registry.claim(script.id, names(script)[0])
        rel = script_file(naming.package(script.folder), module)
        files.setdefault(rel, (source, script.id))
    return problems


# -- watching sources -------------------------------------------------------------

_fingerprints = {}  # script id -> last seen source fingerprint


def _watch_scripts():
    seen = set()
    for script in scripts():
        seen.add(script.id)
        value = script.source_fingerprint()
        if script.id in _fingerprints and _fingerprints[script.id] != value:
            changed(script)
        _fingerprints[script.id] = value
    for script_id in set(_fingerprints) - seen:
        del _fingerprints[script_id]


def changed(script):
    """The script changed: the nodes calling it re-read it, the add-on
    rebuilds."""
    for node in callers(script):
        node.mark_dirty()
    scheduler.request_full()


def register():
    scheduler.add_watcher(_watch_scripts)


def unregister():
    scheduler.remove_watcher(_watch_scripts)
    _fingerprints.clear()
