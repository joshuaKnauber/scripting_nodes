from ...lib.utils.node_tree.scripting_node_trees import (
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
            try:
                bpy.msgbus.subscribe_rna(
                    key=subscribe_to,
                    owner=owner,
                    args=(),
                    notify=on_ntree_name_change,
                )
            except RuntimeError:
                # Class may not be fully registered yet, will be subscribed later
                pass


def unsubscribe_from_name_change():
    bpy.msgbus.clear_by_owner(owner)


def _deferred_register():
    """Deferred registration to ensure all classes are registered first."""
    subscribe_to_name_change()
    return None  # Don't repeat the timer


def register():
    # Defer msgbus subscription to next frame when all classes are registered
    bpy.app.timers.register(_deferred_register, first_interval=0.1)


def unregister():
    unsubscribe_from_name_change()
