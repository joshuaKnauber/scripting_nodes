"""Shared base for Group Input / Group Output nodes - both store a list of
(name, socket_type) items as JSON, and rebuild dynamic sockets to match."""
import json
import bpy

from ...base_node import ScriptingBaseNode
from ._interface import slugify


class GroupInterfaceMixin:
    """Mixin: dynamic sockets driven by a JSON-stored items list.

    Subclasses define:
      items_json: bpy.props.StringProperty(default="[]")
      socket_direction: "INPUT" or "OUTPUT"
      reserved_count: number of fixed sockets at the start (e.g. 1 for the
                      program-flow socket that's always present)
      default_fallback: fallback name slug when user provides empty name
    """

    items_json: bpy.props.StringProperty(default="[]")

    socket_direction = "OUTPUT"  # subclasses override
    reserved_count = 1
    default_fallback = "value"

    def get_items(self):
        try:
            return json.loads(self.items_json)
        except json.JSONDecodeError:
            return []

    def set_items(self, items):
        self.items_json = json.dumps(items)

    def add_item(self, name, socket_type):
        items = self.get_items()
        items.append(
            {"name": slugify(name, self.default_fallback), "type": socket_type}
        )
        self.set_items(items)
        self._sync_sockets()
        self._generate()
        self._notify_call_sites()

    def remove_item(self, index):
        items = self.get_items()
        if 0 <= index < len(items):
            items.pop(index)
            self.set_items(items)
            self._sync_sockets()
            self._generate()
            self._notify_call_sites()

    def _notify_call_sites(self):
        """Re-sync any SNA_Node_Group instances that point at this group tree.

        Cross-tree notification: when a Group Input/Output's interface changes,
        Call Group nodes referencing this tree need their sockets rebuilt and
        their containing trees marked dirty for regeneration.
        """
        if not self.node_tree:
            return
        # Lazy import to avoid circular dependency at module load
        from .....lib.utils.node_tree.scripting_node_trees import (
            scripting_node_trees,
            sn_nodes,
        )
        target_tree = self.node_tree
        for ntree in scripting_node_trees():
            for node in sn_nodes(ntree):
                if (
                    getattr(node, "bl_idname", "") == "SNA_Node_Group"
                    and getattr(node, "node_tree", None) is target_tree
                ):
                    if node._sync_sockets():
                        node._generate()
                        ntree.is_dirty = True

    def _socket_collection(self):
        return self.outputs if self.socket_direction == "OUTPUT" else self.inputs

    def _sync_sockets(self):
        """Rebuild dynamic sockets after the items list changes."""
        sockets = self._socket_collection()
        # Drop everything past the reserved fixed sockets at the front
        while len(sockets) > self.reserved_count:
            sockets.remove(sockets[len(sockets) - 1])
        for item in self.get_items():
            if self.socket_direction == "OUTPUT":
                self.add_output(item["type"], item["name"])
            else:
                self.add_input(item["type"], item["name"])

    def draw(self, context, layout):
        op = layout.operator("sna.add_group_item", text="Add", icon="ADD")
        op.node_id = self.id
        items = self.get_items()
        if items:
            col = layout.column(align=True)
            for i, item in enumerate(items):
                row = col.row(align=True)
                row.label(text=item["name"])
                rop = row.operator("sna.remove_group_item", text="", icon="X")
                rop.node_id = self.id
                rop.index = i


def _poll_group_tree(cls, ntree):
    return (
        ntree.bl_idname == "ScriptingNodeTree"
        and getattr(ntree, "is_group", False)
    )
