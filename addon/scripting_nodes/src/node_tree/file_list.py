"""The add-on's files in the sidebar (Files panel): folders, node trees and
scripts. A UIList needs one collection to list, they're in three, so
`scene.sna.ui.files` has a row per folder, tree and script pointing at it by
id. The rows are synced by a watcher and the list's operators; the UIList
sorts them into the folder hierarchy when it draws (ui/file_list.py).
"""

from typing import NamedTuple

import bpy

from ..core import folders, scheduler
from ..core import scripts as script_list
from ..lib.trees import scripting_node_trees

FOLDER, TREE, SCRIPT = "FOLDER", "TREE", "SCRIPT"


class Entry(NamedTuple):
    kind: str  # FOLDER, TREE or SCRIPT
    item: object  # SNA_TreeFolder, ScriptingNodeTree or SNA_Script

    @property
    def path(self):
        """The folder's path, or the folder a tree or script is in."""
        return self.item.path if self.kind == FOLDER else self.item.folder

    @property
    def name(self):
        if self.kind == SCRIPT:
            return script_list.label(self.item)
        return (
            folders.basename(self.item.path) if self.kind == FOLDER else self.item.name
        )


def _items(settings):
    """{(kind, id): item} of everything the list shows."""
    items = {(FOLDER, f.id): f for f in settings.folders}
    items.update({(TREE, t.id): t for t in scripting_node_trees() if t.id})
    items.update({(SCRIPT, s.id): s for s in settings.scripts if s.id})
    return items


def sync(scene=None):
    """Make the rows match the folders, trees and scripts. Keeps the active
    row."""
    scene = scene or bpy.context.scene
    settings, ui = scene.sna.addon, scene.sna.ui
    folders.sync(settings)
    wanted = list(_items(settings))
    rows = ui.files
    current = [(row.kind, row.item_id) for row in rows]
    if sorted(wanted) == sorted(current):
        return
    index = ui.active_file
    active = current[index] if 0 <= index < len(rows) else None
    rows.clear()
    for kind, item_id in wanted:
        row = rows.add()
        row.kind, row.item_id = kind, item_id
    index = wanted.index(active) if active in wanted else -1
    if ui.active_file != index:
        ui.active_file = index


def row_entry(settings, row) -> Entry | None:
    """What `row` shows, None if it's gone."""
    if not row.item_id:
        return None
    if row.kind == FOLDER:
        item = next((f for f in settings.folders if f.id == row.item_id), None)
    elif row.kind == TREE:
        trees = scripting_node_trees()
        item = next((t for t in trees if t.id == row.item_id), None)
    else:
        item = script_list.find(row.item_id)
    return Entry(row.kind, item) if item is not None else None


def entry(scene, index) -> Entry | None:
    """What row `index` shows, None if it's gone."""
    rows = scene.sna.ui.files
    if not 0 <= index < len(rows):
        return None
    return row_entry(scene.sna.addon, rows[index])


def active(context) -> Entry | None:
    return entry(context.scene, context.scene.sna.ui.active_file)


def target_folder(context) -> str:
    """Where new files and folders go: the active folder, or the folder of
    the active file."""
    selected = active(context)
    return selected.path if selected is not None else ""


def select(context, kind, item):
    """Make the row of `item` active and open the folders above it."""
    sna = context.scene.sna
    # syncing may add folders, which can move `item` in memory
    key, path = (kind, item.id), Entry(kind, item).path
    sync(context.scene)
    above = folders.parent(path) if kind == FOLDER else path
    for ancestor in folders.ancestors(above):
        folder = folders.find(ancestor, sna.addon)
        if folder is not None:
            folder.expanded = True
    rows = [(row.kind, row.item_id) for row in sna.ui.files]
    if key in rows:
        sna.ui.active_file = rows.index(key)


def layout_rows(scene, filter_name=""):
    """For each row: (sort key, depth, visible), the order of the hierarchy:
    folders first, then files, by name. With a filter, the files whose name
    matches and the folders above them."""
    pattern = filter_name.lower().strip("*")
    expanded = {f.path: f.expanded for f in scene.sna.addon.folders}
    items = _items(scene.sna.addon)
    entries = []
    for row in scene.sna.ui.files:
        item = items.get((row.kind, row.item_id))
        entries.append(Entry(row.kind, item) if item is not None else None)
    matches = set()  # folders above a matching file
    for e in entries:
        if e is not None and e.kind != FOLDER and pattern in e.name.lower():
            matches.update(folders.ancestors(e.path))

    result = []
    for e in entries:
        if e is None:
            result.append(((), 0, False))
            continue
        is_folder = e.kind == FOLDER
        above = folders.ancestors(folders.parent(e.path) if is_folder else e.path)
        key = tuple((0, part.lower()) for part in folders.split(e.path))
        if not is_folder:
            key += ((1, e.name.lower()),)
        if pattern:
            visible = e.path in matches if is_folder else pattern in e.name.lower()
        else:
            visible = all(expanded.get(a, True) for a in above)
        result.append((key, len(above), visible))
    return result


def _watch():
    # files are added and removed outside the list too (header, Outliner,
    # append, undo, MCP)
    scene = bpy.context.scene
    if scene is not None and hasattr(scene, "sna"):
        sync(scene)


def register():
    scheduler.add_watcher(_watch)


def unregister():
    scheduler.remove_watcher(_watch)
