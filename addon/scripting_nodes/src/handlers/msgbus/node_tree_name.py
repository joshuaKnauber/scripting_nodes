from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
)
import bpy

owner = object()


def on_ntree_name_change():
    bpy.context.scene.sna.is_dirty = True
    for ntree in scripting_node_trees():
        ntree.is_dirty = True


def subscribe_to_name_change():
    unsubscribe_from_name_change()
    for cls in bpy.types.NodeTree.__subclasses__():
        if getattr(cls, "is_sn", False):
            subscribe_to = (cls, "name")
            bpy.msgbus.subscribe_rna(
                key=subscribe_to,
                owner=owner,
                args=(),
                notify=on_ntree_name_change,
            )


def unsubscribe_from_name_change():
    bpy.msgbus.clear_by_owner(owner)


def register():
    subscribe_to_name_change()


def unregister():
    unsubscribe_from_name_change()
