"""Asset: the path of one of the add-on's assets (Addon Data › Assets,
core/assets.py) in the installed add-on."""

import bpy

from ....core import assets as asset_list
from ....core.context import NodeError
from ....sockets.spec import String
from ...base_node import ScriptingBaseNode


def _choices():
    """(label, asset) of the list's assets, labels unique."""
    names = asset_list.file_names()
    return [(names[asset.id], asset) for asset in asset_list.assets()]


def _get_asset(self):
    asset = asset_list.find(self.asset_id)
    return asset_list.file_names().get(asset.id, "") if asset else ""


def _set_asset(self, value):
    asset = next((a for label, a in _choices() if label == value), None)
    if value and asset is None:
        return  # text that isn't a choice keeps the current one
    self.asset_id = asset.id if asset else ""
    self.mark_dirty()


def _search_asset(self, context, edit_text):
    return [label for label, _ in _choices()]


class SNA_Node_Asset(ScriptingBaseNode, bpy.types.Node):
    """The path of a file or folder of the add-on's assets (Addon Data ›
    Assets): they ship with the add-on in its `assets` folder."""

    bl_idname = "SNA_Node_Asset"
    bl_label = "Asset"
    bl_width_default = 200
    sn_outputs = [String("path", "Path")]

    asset_id: bpy.props.StringProperty(options={"HIDDEN"})
    asset: bpy.props.StringProperty(
        name="Asset",
        description="File or folder of the add-on's assets (Addon Data › Assets)",
        get=_get_asset,
        set=_set_asset,
        search=_search_asset,
    )

    def asset_item(self):
        return asset_list.find(self.asset_id)

    def draw(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "asset", text="", icon="FILE")
        row.operator("sna.add_asset", text="", icon="ADD").node_id = self.id

    def emit(self, ctx):
        asset = self.asset_item()
        if asset is None:
            if self.asset_id:
                raise NodeError("The asset was removed from the add-on")
            raise NodeError("Pick an asset")
        problem = asset_list.problem(asset)
        if problem:
            raise NodeError(problem)
        name = asset_list.file_names()[asset.id]
        folder = repr(asset_list.FOLDER)
        ctx.output("path", f"os.path.join({ctx.addon_folder()}, {folder}, {name!r})")
