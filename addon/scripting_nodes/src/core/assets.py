"""The add-on's assets (Addon Data › Assets, `scene.sna.addon.assets`): files
and folders shipped with the add-on in `assets/`, the live one and exports
alike. Asset nodes give their path in the installed add-on.

An asset's name is its name in `assets/` (made unique). Its files aren't read
into memory: the compiler puts a `FileCopy` in the add-on's files, which the
runtime copies when the size or modification time changed.
"""

import os
import shutil

import bpy

from ..lib.trees import scripting_node_trees, sn_nodes
from . import scheduler

FOLDER = "assets"
ASSET_NODE = "SNA_Node_Asset"
_SKIP = {"__pycache__", ".DS_Store", "Thumbs.db"}


class FileCopy:
    """A file of the add-on copied from `source`. Equal to another copy (the
    one in the add-on's folder) when size and modification time match:
    shutil.copy2 keeps the modification time (to the microsecond)."""

    __slots__ = ("source", "size", "mtime")

    def __init__(self, source):
        stat = os.stat(source)
        self.source = source
        # microseconds: what copies keep on macOS (shutil.copy2)
        self.size, self.mtime = stat.st_size, stat.st_mtime_ns // 1000

    def __eq__(self, other):
        return isinstance(other, FileCopy) and (self.size, self.mtime) == (
            other.size,
            other.mtime,
        )

    def __hash__(self):
        return hash((self.size, self.mtime))

    def __repr__(self):
        return f"FileCopy({self.source!r})"

    def read(self) -> bytes:
        with open(self.source, "rb") as f:
            return f.read()

    def copy_to(self, path):
        if os.path.abspath(self.source) != os.path.abspath(path):
            shutil.copy2(self.source, path)


def contents(value) -> str | bytes:
    """What a file of the add-on contains (str, bytes or a FileCopy)."""
    return value.read() if isinstance(value, FileCopy) else value


# -- the list ---------------------------------------------------------------------


def assets():
    scene = bpy.context.scene
    return scene.sna.addon.assets if scene is not None else []


def find(asset_id):
    if not asset_id:
        return None
    return next((a for a in assets() if a.id == asset_id), None)


def source(asset) -> str | None:
    """Absolute path of the file or folder, None if not set."""
    if not asset.filepath:
        return None
    return os.path.normpath(bpy.path.abspath(asset.filepath))


def clean_name(name: str) -> str:
    """A file name: no separators, no surrounding spaces or dots."""
    for char in '/\\:*?"<>|':
        name = name.replace(char, "_")
    return name.strip().strip(".")


def file_names() -> dict[str, str]:
    """{asset id: name in assets/}, unique (ignoring case: file systems of
    macOS and Windows do)."""
    names, taken = {}, set()
    for asset in assets():
        base = clean_name(asset.name) or "asset"
        stem, dot, ext = base.rpartition(".")
        if not dot or not stem:
            stem, dot, ext = base, "", ""
        name, i = base, 2
        while name.lower() in taken:
            name, i = f"{stem}_{i}{dot}{ext}", i + 1
        taken.add(name.lower())
        names[asset.id] = name
    return names


def problem(asset) -> str | None:
    """Why `asset` can't be shipped, None if it can."""
    path = source(asset)
    if path is None:
        return "Pick a file or folder"
    if asset.filepath.startswith("//") and not bpy.data.filepath:
        return "Save the .blend file first (the path is relative to it)"
    if not os.path.exists(path):
        return f"{path} doesn't exist"
    return None


def add_to_addon(files) -> dict[str, str]:
    """Add the assets' files to `files` ({rel: FileCopy}). Returns {asset
    id: error} of those that can't be added."""
    problems = {}
    names = file_names()
    for asset in assets():
        message = problem(asset)
        if message:
            problems[asset.id] = message
            continue
        path, rel = source(asset), f"{FOLDER}/{names[asset.id]}"
        try:
            if os.path.isfile(path):
                files[rel] = FileCopy(path)
                continue
            for root, dirs, entries in os.walk(path):
                dirs[:] = sorted(d for d in dirs if d not in _SKIP)
                for name in sorted(entries):
                    if name in _SKIP:
                        continue
                    full = os.path.join(root, name)
                    sub = os.path.relpath(full, path).replace(os.sep, "/")
                    files[f"{rel}/{sub}"] = FileCopy(full)
        except OSError as exc:
            problems[asset.id] = f"Can't read {path}: {exc.strerror or exc}"
    return problems


def users(asset):
    """Asset nodes picking `asset`."""
    return [
        node
        for tree in scripting_node_trees()
        for node in sn_nodes(tree)
        if node.bl_idname == ASSET_NODE and node.asset_id == asset.id
    ]


def changed(asset):
    """The asset's source or name changed: rebuild (nodes using it too)."""
    for node in users(asset):
        node.mark_dirty()
    _fingerprints.pop(asset.id, None)
    scheduler.request_full()


# -- watching sources -------------------------------------------------------------

_fingerprints = {}  # asset id -> last seen fingerprint


def fingerprint(asset):
    """Changes whenever a file of the asset changes, is added or removed."""
    path = source(asset)
    if path is None:
        return None
    try:
        if os.path.isfile(path):
            stat = os.stat(path)
            return (stat.st_size, stat.st_mtime_ns)
        result = []
        for root, dirs, names in os.walk(path):
            dirs[:] = sorted(d for d in dirs if d not in _SKIP)
            for name in sorted(names):
                stat = os.stat(os.path.join(root, name))
                result.append((root, name, stat.st_size, stat.st_mtime_ns))
        return hash(tuple(result)) if os.path.isdir(path) else None
    except OSError:
        return None


def _watch_assets():
    for asset in assets():
        current = fingerprint(asset)
        if _fingerprints.get(asset.id, current) != current:
            scheduler.request_full()
        _fingerprints[asset.id] = current


def register():
    scheduler.add_watcher(_watch_assets)


def unregister():
    scheduler.remove_watcher(_watch_assets)
