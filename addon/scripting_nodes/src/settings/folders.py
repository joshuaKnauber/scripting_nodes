"""Folders of the tree list (`scene.sna.addon.folders`, core/folders.py)."""

import bpy

from ..core import folders, scheduler


def _get_name(self):
    return folders.basename(self.path)


def _set_name(self, value):
    name = folders.clean_name(value)
    if not name or name == _get_name(self):
        return
    settings = self.id_data.sna.addon
    path = folders.join(folders.parent(self.path), name)
    folders.move(self.path, folders.unique_path(path, settings), settings)
    scheduler.request_full()


class SNA_TreeFolder(bpy.types.PropertyGroup):
    """A folder of node trees: a package of the add-on."""

    id: bpy.props.StringProperty(options={"HIDDEN"})
    # e.g. "UI/Panels", trees in it have it as `tree.folder`
    path: bpy.props.StringProperty(options={"HIDDEN"})
    name: bpy.props.StringProperty(
        name="Name",
        description="Name of the folder (its package in the add-on)",
        get=_get_name,
        set=_set_name,
    )
    expanded: bpy.props.BoolProperty(
        name="Expanded", description="Show the contents of the folder", default=True
    )
