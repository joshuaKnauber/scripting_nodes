import bpy

from ...core import scheduler

owner = object()


def on_ntree_name_change():
    # Tree names are part of module names and reference display names
    scheduler.request_full()


def subscribe_to_name_change():
    unsubscribe_from_name_change()
    from ...node_tree.node_tree import ScriptingNodeTree

    for key in ((ScriptingNodeTree, "name"), (bpy.types.Node, "name")):
        bpy.msgbus.subscribe_rna(
            key=key, owner=owner, args=(), notify=on_ntree_name_change
        )


def unsubscribe_from_name_change():
    bpy.msgbus.clear_by_owner(owner)


def register():
    subscribe_to_name_change()


def unregister():
    unsubscribe_from_name_change()
