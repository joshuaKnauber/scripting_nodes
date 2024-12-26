from .is_sn import is_sn
import bpy


def scripting_node_trees():
    return [ntree for ntree in bpy.data.node_trees if is_sn(ntree)]
