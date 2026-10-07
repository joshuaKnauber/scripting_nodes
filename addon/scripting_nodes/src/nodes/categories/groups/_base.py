"""Shared base for Group Input / Group Output: a list of (name, socket type)
items stored as JSON. Each item is one socket (parameter or return value)."""

import json

import bpy

from ....lib.trees import scripting_node_trees, sn_nodes
from ....sockets.spec import Socket
from ._interface import slugify


class GroupInterfaceMixin:
    items_json: bpy.props.StringProperty(default="[]")

    default_fallback = "value"
    ITEM_PREFIX = "item_"

    def get_items(self):
        try:
            return json.loads(self.items_json)
        except json.JSONDecodeError:
            return []

    def set_items(self, items):
        self.items_json = json.dumps(items)

    def item_specs(self):
        return [
            Socket(item["type"], self.ITEM_PREFIX + item["name"], item["name"])
            for item in self.get_items()
        ]

    def parameter_names(self):
        return [item["name"] for item in self.get_items()]

    def parameter_keys(self):
        return [self.ITEM_PREFIX + item["name"] for item in self.get_items()]

    def add_item(self, name, socket_type):
        items = self.get_items()
        names = {item["name"] for item in items}
        name = slugify(name, self.default_fallback)
        base, i = name, 2
        while name in names:
            name, i = f"{base}_{i}", i + 1
        items.append({"name": name, "type": socket_type})
        self.set_items(items)
        self._notify_call_sites()

    def remove_item(self, index):
        items = self.get_items()
        if 0 <= index < len(items):
            items.pop(index)
            self.set_items(items)
            self._notify_call_sites()

    def _notify_call_sites(self):
        """Group nodes calling this tree need their sockets updated."""
        for tree in scripting_node_trees():
            for node in sn_nodes(tree):
                if (
                    node.bl_idname == "SNA_Node_Group"
                    and node.node_tree == self.id_data
                ):
                    node.mark_dirty()

    def draw(self, context, layout):
        op = layout.operator("sna.add_group_item", text="Add", icon="ADD")
        op.node_id = self.id
        items = self.get_items()
        if items:
            col = layout.column(align=True)
            for i, item in enumerate(items):
                row = col.row(align=True)
                row.label(text=item["name"])
                remove = row.operator("sna.remove_group_item", text="", icon="X")
                remove.node_id = self.id
                remove.index = i


def _poll_group_tree(cls, ntree):
    return ntree.bl_idname == "ScriptingNodeTree" and getattr(ntree, "is_group", False)
