from scripting_nodes import auto_load
from scripting_nodes.src.lib.constants.paths import NODES_FOLDER
import inspect
import os
import bpy


def get_node_categories():
    for cls in auto_load.ordered_classes:
        if cls.bl_rna.base and cls.bl_rna.base.identifier == "Node":
            path = os.path.dirname(inspect.getfile(cls))
            dirs = path.split(os.sep)
            print(dirs)


def append_node_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.label(text="Scripting Nodes", icon="NODETREE")
    get_node_categories()


def register():
    bpy.types.NODE_MT_add.append(append_node_menu)
