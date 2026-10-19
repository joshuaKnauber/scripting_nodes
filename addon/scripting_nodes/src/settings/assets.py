"""The add-on's assets (Addon Data › Assets, core/assets.py): files and
folders shipped in the add-on's `assets` folder."""

import os

import bpy
from bpy_extras.io_utils import ImportHelper

from ..core import assets as asset_list
from ..core import errors, scheduler
from ..lib.ids import get_short_id
from ..lib.trees import node_by_id


def _filepath_changed(self, context):
    path = asset_list.source(self)
    if path and not self.name:
        self.name = os.path.basename(path.rstrip(os.sep))
    asset_list.changed(self)


def _name_changed(self, context):
    asset_list.changed(self)


class SNA_Asset(bpy.types.PropertyGroup):
    """A file or folder shipped with the add-on in `assets/`."""

    id: bpy.props.StringProperty(options={"HIDDEN"})
    name: bpy.props.StringProperty(
        name="Name",
        description="Name of the file or folder in the add-on's assets folder",
        update=_name_changed,
    )
    filepath: bpy.props.StringProperty(
        name="Source",
        description="File or folder that is copied into the add-on",
        subtype="FILE_PATH",
        update=_filepath_changed,
    )


class SNA_OT_AddAsset(bpy.types.Operator, ImportHelper):
    """Add a file or a folder to the add-on's assets"""

    bl_idname = "sna.add_asset"
    bl_label = "Add Asset"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    folder: bpy.props.BoolProperty(
        name="Whole Folder",
        description="Add the folder the file browser shows instead of a file",
    )
    relative_path: bpy.props.BoolProperty(
        name="Relative Path",
        description="Store the path relative to the .blend file",
        default=True,
    )
    # an Asset node that picks the new asset
    node_id: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "folder")
        row = layout.row()
        row.active = bool(bpy.data.filepath)
        row.prop(self, "relative_path")

    def execute(self, context):
        path = os.path.dirname(self.filepath) if self.folder else self.filepath
        if not os.path.exists(path):
            self.report({"ERROR"}, f"{path} doesn't exist")
            return {"CANCELLED"}
        addon = context.scene.sna.addon
        asset = addon.assets.add()
        asset.id = get_short_id()
        asset.name = os.path.basename(path.rstrip(os.sep))
        if self.relative_path and bpy.data.filepath:
            try:
                path = bpy.path.relpath(path)
            except ValueError:
                pass  # another drive (Windows)
        asset.filepath = path
        addon.active_asset = len(addon.assets) - 1
        node = node_by_id(self.node_id)
        if node is not None:
            node.asset_id = asset.id
            node.mark_dirty()
        scheduler.request_full()
        return {"FINISHED"}


class SNA_OT_RemoveAsset(bpy.types.Operator):
    """Remove the selected asset from the add-on (its file stays)"""

    bl_idname = "sna.remove_asset"
    bl_label = "Remove Asset"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        addon = context.scene.sna.addon
        return 0 <= addon.active_asset < len(addon.assets)

    def execute(self, context):
        addon = context.scene.sna.addon
        index = addon.active_asset
        users = asset_list.users(addon.assets[index])
        addon.assets.remove(index)
        addon.active_asset = min(index, len(addon.assets) - 1)
        for node in users:
            node.mark_dirty()
        scheduler.request_full()
        return {"FINISHED"}


class SNA_OT_AddAssetNode(bpy.types.Operator):
    """Add an Asset node giving the path of this asset"""

    bl_idname = "sna.add_asset_node"
    bl_label = "Add Asset Node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    asset_id: bpy.props.StringProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return getattr(context.space_data, "edit_tree", None) is not None

    def execute(self, context):
        if asset_list.find(self.asset_id) is None:
            return {"CANCELLED"}
        bpy.ops.node.add_node(
            "INVOKE_DEFAULT", type=asset_list.ASSET_NODE, use_transform=True
        )
        node = context.space_data.edit_tree.nodes.active
        node.asset_id = self.asset_id
        node.mark_dirty()
        return {"FINISHED"}


class SNA_UL_Assets(bpy.types.UIList):
    bl_idname = "SNA_UL_Assets"

    def draw_item(self, context, layout, data, item, icon, active_data, prop):
        path = asset_list.source(item)
        is_folder = path is not None and os.path.isdir(path)
        row = layout.row(align=True)
        row.prop(
            item,
            "name",
            text="",
            emboss=False,
            icon="FILE_FOLDER" if is_folder else "FILE",
        )
        if errors.node_message(item.id):
            row.label(text="", icon="ERROR")


def draw_assets(layout, context):
    """The Assets panel: the list, the selected asset's source and the nodes
    using it."""
    addon = context.scene.sna.addon
    row = layout.row()
    row.template_list(
        "SNA_UL_Assets", "", addon, "assets", addon, "active_asset", rows=3
    )
    col = row.column(align=True)
    col.operator("sna.add_asset", text="", icon="ADD")
    col.operator("sna.remove_asset", text="", icon="REMOVE")
    if not 0 <= addon.active_asset < len(addon.assets):
        return
    asset = addon.assets[addon.active_asset]
    col = layout.column()
    col.prop(asset, "filepath", text="")
    name = asset_list.file_names().get(asset.id, "")
    sub = col.row()
    sub.active = False
    sub.label(text=f"{asset_list.FOLDER}/{name}")
    message = errors.node_message(asset.id)
    if message:
        box = layout.box()
        box.alert = True
        box.label(text=message, icon="ERROR")
    op = layout.operator("sna.add_asset_node", text="Add Node", icon="ADD")
    op.asset_id = asset.id
    users = asset_list.users(asset)
    if users:
        box = layout.box()
        col = box.column(align=True)
        for node in users:
            row = col.row(align=True)
            row.label(text=node.label or node.bl_label, icon="NODE")
            row.label(text=f"[{node.id_data.name}]")
            op = row.operator("sna.go_to_node", text="", icon="VIEWZOOM")
            op.node_id = node.id
