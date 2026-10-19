"""Folders of the add-on's files, node trees and scripts: `tree.folder` /
`script.folder` is a path like "UI/Panels" ("" is the top level). A folder
is a package of the generated add-on, its files are modules in it
(`ui/panels/main.py`, names in core/naming.py).

The folder list of the add-on (`scene.sna.addon.folders`) keeps folders
without files and whether they're open in the tree list; folders of files
that aren't in it (appended trees) are added by `sync()`.
"""

import bpy

from ..lib.ids import get_short_id
from ..lib.trees import scripting_node_trees

SEPARATOR = "/"


def split(path: str) -> list[str]:
    return [part for part in path.split(SEPARATOR) if part]


def join(*parts: str) -> str:
    return SEPARATOR.join(part for part in parts if part)


def parent(path: str) -> str:
    return path.rpartition(SEPARATOR)[0]


def basename(path: str) -> str:
    return path.rpartition(SEPARATOR)[2]


def ancestors(path: str) -> list[str]:
    """ "A/B/C" -> ["A", "A/B", "A/B/C"]."""
    parts = split(path)
    return [join(*parts[: i + 1]) for i in range(len(parts))]


def is_inside(path: str, folder: str) -> bool:
    """`path` is `folder` or in it."""
    return path == folder or path.startswith(folder + SEPARATOR)


def clean_name(name: str) -> str:
    """A folder name: no separators, no surrounding spaces."""
    return name.replace(SEPARATOR, " ").strip()


def addon_folders(settings=None):
    if settings is None:
        settings = bpy.context.scene.sna.addon
    return settings.folders


def find(path: str, settings=None):
    for folder in addon_folders(settings):
        if folder.path == path:
            return folder
    return None


def files(settings=None, trees=None) -> list:
    """What can be in a folder: node trees and the add-on's scripts."""
    if settings is None:
        settings = bpy.context.scene.sna.addon
    if trees is None:
        trees = scripting_node_trees()
    return [*trees, *settings.scripts]


def paths(settings=None, trees=None) -> list[str]:
    """Every folder: listed ones, folders of files, and their parents."""
    found = set()
    for path in [f.path for f in addon_folders(settings)] + [
        file.folder for file in files(settings, trees)
    ]:
        found.update(ancestors(path))
    return sorted(found)


def unique_path(path: str, settings=None, trees=None) -> str:
    """`path`, else "<path> 2", "<path> 3", ... if a folder has that path."""
    taken = set(paths(settings, trees))
    candidate, i = path, 2
    while candidate in taken:
        candidate, i = f"{path} {i}", i + 1
    return candidate


def add(path: str, settings=None):
    """Add `path` (and its parents) to the folder list."""
    for ancestor in ancestors(path):
        if find(ancestor, settings) is None:
            _new(ancestor, settings)
    return find(path, settings)


def _new(path, settings):
    folder = addon_folders(settings).add()
    folder.id = get_short_id()
    folder.path = path


def sync(settings=None, trees=None) -> bool:
    """Add folders of files that aren't listed. True if something changed."""
    listed = {f.path for f in addon_folders(settings)}
    missing = [path for path in paths(settings, trees) if path not in listed]
    for path in missing:
        _new(path, settings)
    return bool(missing)


def move(old: str, new: str, settings=None, trees=None):
    """Move (or rename) folder `old` with its contents to `new`."""
    for file in files(settings, trees):
        if is_inside(file.folder, old):
            file.folder = new + file.folder[len(old) :]
    for folder in addon_folders(settings):
        if is_inside(folder.path, old):
            folder.path = new + folder.path[len(old) :]


def remove(path: str, settings=None, trees=None):
    """Remove folder `path`, its contents move to its parent."""
    up = parent(path)
    for file in files(settings, trees):
        if file.folder == path:
            file.folder = up
    folders = addon_folders(settings)
    for i in reversed(range(len(folders))):
        if folders[i].path == path:
            folders.remove(i)
    # subfolders keep their names in the parent (made unique if taken)
    for folder in list(folders):
        if parent(folder.path) == path:
            target = unique_path(join(up, basename(folder.path)), settings, trees)
            move(folder.path, target, settings, trees)
