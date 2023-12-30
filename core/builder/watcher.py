import bpy

from . import builder


def watch_addon():
    sn = bpy.context.scene.sna
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_dirty", False):
            _unmark_dirty()
            builder.build_addon(
                prod_build=sn.production_build, module=builder.dev_module()
            )
            return 0.5
    return 0.1


def _unmark_dirty():
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn_ntree", False):
            ntree.is_dirty = False
