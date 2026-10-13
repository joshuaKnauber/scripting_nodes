"""Operators of the data explorer (blend_data/explorer.py). Moving around
only changes the explorer; nodes change through Add Node, Go to Its Path and
Use This Path."""

import bpy

from .. import explorer
from .paths import SNA_OT_PasteBlenderPath


def location(context):
    return explorer.free_location(context.scene.sna.ui.explorer_path)


def selected_node(context):
    """The active node if it has a Blender data path, else None."""
    tree = getattr(context.space_data, "edit_tree", None)
    node = tree.nodes.active if tree is not None else None
    if node is None or not node.select or not explorer.uses_paths(node):
        return None
    return node


def go(context, target):
    ui = context.scene.sna.ui
    ui.explorer_filter = ""
    ui.explorer_path = target.python() if target.root else ""


class _Target:
    """An entry at the current location: an attribute (`member`), an item of
    a collection (`item_mode`), or a root (`root`)."""

    member: bpy.props.StringProperty(options={"SKIP_SAVE"})
    item_mode: bpy.props.EnumProperty(
        items=[("NONE", "None", ""), ("INDEX", "Index", ""), ("NAME", "Name", "")],
        options={"SKIP_SAVE"},
    )
    item_name: bpy.props.StringProperty(options={"SKIP_SAVE"})
    item_index: bpy.props.IntProperty(options={"SKIP_SAVE"})
    root: bpy.props.StringProperty(options={"SKIP_SAVE"})

    def target(self, current):
        if self.root:
            return explorer.Location(self.root)
        if self.item_mode != "NONE":
            value = self.item_name if self.item_mode == "NAME" else self.item_index
            return current.extended(key=explorer.Key(self.item_mode, value))
        return current.extended(self.member)


class SNA_OT_ExplorerOpen(_Target, bpy.types.Operator):
    """Show what's in this entry"""

    bl_idname = "sna.explorer_open"
    bl_label = "Open"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        go(context, self.target(location(context)))
        return {"FINISHED"}


class SNA_OT_ExplorerBack(bpy.types.Operator):
    """Go back"""

    bl_idname = "sna.explorer_back"
    bl_label = "Back"
    bl_options = {"INTERNAL"}

    # segments to keep; -1: the start (Context / Blend File)
    count: bpy.props.IntProperty(default=-1, options={"SKIP_SAVE"})

    def execute(self, context):
        current = location(context)
        if self.count < 0:
            go(context, explorer.Location(""))
        else:
            go(context, current.truncated(self.count))
        return {"FINISHED"}


class SNA_OT_ExplorerAdd(_Target, bpy.types.Operator):
    """Add a Blender Data node with the path of this entry"""

    bl_idname = "sna.explorer_add"
    bl_label = "Add Node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return SNA_OT_PasteBlenderPath.poll(context)

    def execute(self, context):
        target = self.target(location(context))
        tree = context.space_data.edit_tree
        node = tree.nodes.new("SNA_Node_BlendData")
        node.location = _view_center(context)
        node.path_root = target.root
        explorer.set_node_location(node, target)
        for other in tree.nodes:
            other.select = other == node
        tree.nodes.active = node
        return {"FINISHED"}


class SNA_OT_ExplorerGoToNode(bpy.types.Operator):
    """Show the data at the end of the selected node's path"""

    bl_idname = "sna.explorer_go_to_node"
    bl_label = "Go to Its Path"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return selected_node(context) is not None

    def execute(self, context):
        try:
            target = explorer.absolute_location(selected_node(context))
        except explorer.Unavailable as error:
            self.report({"WARNING"}, str(error))
            return {"CANCELLED"}
        go(context, target)
        return {"FINISHED"}


class SNA_OT_ExplorerUseForNode(bpy.types.Operator):
    """Set the selected node's path to where the explorer is"""

    bl_idname = "sna.explorer_use_for_node"
    bl_label = "Use This Path"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return selected_node(context) is not None and location(context).root

    def execute(self, context):
        explorer.apply_to_node(selected_node(context), location(context))
        return {"FINISHED"}


def _view_center(context):
    region = next((r for r in context.area.regions if r.type == "WINDOW"), None)
    if region is None:
        return (0, 0)
    return region.view2d.region_to_view(region.width / 2, region.height / 2)
