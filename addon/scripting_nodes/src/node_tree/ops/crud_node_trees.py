"""Operators of the Files list: add node trees, scripts and folders, remove
and move them (node_tree/file_list.py)."""

import bpy

from ...core import folders, scheduler
from ...core import scripts as script_list
from ...lib.ids import get_short_id
from .. import file_list
from ..file_list import FOLDER, SCRIPT, TREE
from ..node_tree import ScriptingNodeTree

TOP_LEVEL = "/"  # the "folder" of files in no folder (paths never start with /)


class SNA_OT_AddNodeTree(bpy.types.Operator):
    """Add a node tree (a module of the add-on) to the selected folder"""

    bl_idname = "sna.add_node_tree"
    bl_label = "Add Node Tree"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context: bpy.types.Context):
        ntree = bpy.data.node_groups.new("Node Tree", ScriptingNodeTree.bl_idname)
        ntree.init()
        ntree.folder = file_list.target_folder(context)
        if context.space_data and context.space_data.type == "NODE_EDITOR":
            context.space_data.node_tree = ntree
        file_list.select(context, TREE, ntree)
        scheduler.request_full()
        return {"FINISHED"}


class SNA_OT_AddScript(bpy.types.Operator):
    """Add a script (a module of the add-on, your code unchanged) to the
    selected folder"""

    bl_idname = "sna.add_script"
    bl_label = "Add Script"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        folder = file_list.target_folder(context)
        script = context.scene.sna.addon.scripts.add()
        script.id = get_short_id()
        script.folder = folder
        file_list.select(context, SCRIPT, script)
        scheduler.request_full()
        return {"FINISHED"}


class SNA_OT_AddFolder(bpy.types.Operator):
    """Add a folder (a package of the add-on) to the selected folder"""

    bl_idname = "sna.add_folder"
    bl_label = "Add Folder"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        path = folders.join(file_list.target_folder(context), "New Folder")
        folder = folders.add(folders.unique_path(path))
        file_list.select(context, FOLDER, folder)
        return {"FINISHED"}


class SNA_OT_RemoveFile(bpy.types.Operator):
    bl_idname = "sna.remove_file"
    bl_label = "Remove"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def description(cls, context, properties):
        selected = file_list.active(context)
        if selected is not None and selected.kind == FOLDER:
            return "Remove the selected folder, its contents move to the folder above"
        if selected is not None and selected.kind == SCRIPT:
            return "Remove the selected script from the add-on (its text stays)"
        return "Remove the selected node tree"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return file_list.active(context) is not None

    def execute(self, context: bpy.types.Context):
        selected = file_list.active(context)
        if selected.kind == FOLDER:
            folders.remove(selected.item.path)
        elif selected.kind == TREE:
            bpy.data.node_groups.remove(selected.item)
        else:
            scripts = context.scene.sna.addon.scripts
            callers = script_list.callers(selected.item)
            script_id = selected.item.id
            scripts.remove(next(i for i, s in enumerate(scripts) if s.id == script_id))
            for node in callers:
                node.mark_dirty()
        # select the row now at its place in the list
        ui = context.scene.sna.ui
        index = ui.active_file
        file_list.sync(context.scene)
        ui.active_file = min(index, len(ui.files) - 1)
        scheduler.request_full()
        return {"FINISHED"}


_folder_items = []  # Blender needs Python to keep dynamic enum strings


def _folders(self, context):
    """Folders the selected file or folder can move to."""
    selected = file_list.active(context)
    _folder_items.clear()
    _folder_items.append((TOP_LEVEL, "Top Level", "Not in a folder", "FILE_PARENT", 0))
    for i, path in enumerate(folders.paths(), start=1):
        if (
            selected
            and selected.kind == FOLDER
            and folders.is_inside(path, selected.path)
        ):
            continue
        label = "    " * (len(folders.split(path)) - 1) + folders.basename(path)
        _folder_items.append((path, label, path, "FILE_FOLDER", i))
    return _folder_items


class SNA_OT_MoveToFolder(bpy.types.Operator):
    """Move the selected file or folder into a folder"""

    bl_idname = "sna.move_to_folder"
    bl_label = "Move to Folder"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    folder: bpy.props.EnumProperty(name="Folder", items=_folders)

    @classmethod
    def poll(cls, context):
        return file_list.active(context) is not None

    def execute(self, context):
        kind, item = file_list.active(context)
        target = "" if self.folder == TOP_LEVEL else self.folder
        if kind == FOLDER:
            if folders.is_inside(target, item.path):
                return {"CANCELLED"}
            if folders.parent(item.path) != target:
                path = folders.join(target, folders.basename(item.path))
                folders.move(item.path, folders.unique_path(path))
        else:
            item.folder = target
        file_list.select(context, kind, item)
        scheduler.request_full()
        return {"FINISHED"}
