from .is_sn import is_sn
import bpy


def scripting_node_trees():
    return [ntree for ntree in bpy.data.node_groups if is_sn(ntree)]


def has_addon():
    return len(scripting_node_trees()) > 0
