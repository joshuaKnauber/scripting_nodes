"""
Timer-based watcher for node tree interface changes.

This monitors changes to the interface items (sockets) in group trees
and triggers socket synchronization when changes are detected.
"""

from ...lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
)
import bpy


def watch_interface_changes():
    """Check for interface changes in all group trees and sync sockets."""
    try:
        for tree in scripting_node_trees():
            if getattr(tree, "is_group", False):
                # This will check if interface changed and sync if needed
                tree.update_group_sockets()
    except Exception:
        # Silently ignore errors during polling
        pass

    # Poll every 0.1 seconds for responsive updates
    return 0.1


def register():
    if not bpy.app.timers.is_registered(watch_interface_changes):
        bpy.app.timers.register(watch_interface_changes)


def unregister():
    if bpy.app.timers.is_registered(watch_interface_changes):
        bpy.app.timers.unregister(watch_interface_changes)
