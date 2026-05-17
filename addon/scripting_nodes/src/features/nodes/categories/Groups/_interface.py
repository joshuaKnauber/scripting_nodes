"""Operators shared by Group Input / Group Output nodes for managing their
parameter / return-value lists."""
import re
import bpy

from .....lib.utils.node_tree.scripting_node_trees import node_by_id
from ....sockets.socket_types import DATA_SOCKET_ENUM_ITEMS


def slugify(name, fallback):
    """Convert a display name to a valid Python identifier."""
    s = re.sub(r"[^a-zA-Z0-9_]", "_", (name or "").strip())
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = fallback
    if s[0].isdigit():
        s = "_" + s
    return s


def _mark_dirty(node):
    """Force the tree to regenerate after the interface changes."""
    if node and node.node_tree:
        node.node_tree.is_dirty = True


class SNA_OT_AddGroupItem(bpy.types.Operator):
    """Add a parameter (on Group Input) or return value (on Group Output)."""

    bl_idname = "sna.add_group_item"
    bl_label = "Add"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    item_name: bpy.props.StringProperty(name="Name", default="value")
    item_type: bpy.props.EnumProperty(
        items=DATA_SOCKET_ENUM_ITEMS,
        name="Type",
        default="ScriptingDataSocket",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "item_name")
        layout.prop(self, "item_type")

    def execute(self, context):
        node = node_by_id(self.node_id)
        if not node or not hasattr(node, "add_item"):
            return {"CANCELLED"}
        node.add_item(self.item_name, self.item_type)
        _mark_dirty(node)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)


class SNA_OT_RemoveGroupItem(bpy.types.Operator):
    """Remove a parameter / return value by index."""

    bl_idname = "sna.remove_group_item"
    bl_label = "Remove"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if not node or not hasattr(node, "remove_item"):
            return {"CANCELLED"}
        node.remove_item(self.index)
        _mark_dirty(node)
        return {"FINISHED"}
