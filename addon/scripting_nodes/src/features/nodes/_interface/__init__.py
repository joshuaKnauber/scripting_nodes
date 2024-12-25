import bpy
from .add_menu import append_node_menu


def register():
    bpy.types.NODE_MT_add.append(append_node_menu)
