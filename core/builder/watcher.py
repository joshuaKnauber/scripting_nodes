import bpy

from . import builder


def watch_addon():
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_dirty", False):
            _unmark_dirty()
            builder.build_addon()
            return 0.5
    return 0.1


def _unmark_dirty():
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn_ntree", False):
            ntree.is_dirty = False
