from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
)
from .ui_settings.ui_properties import SNA_UISettings
from .sn_settings.dev_properties import SNA_DevSettings
from .addon_settings.addon_properties import SNA_AddonSettings
import bpy


class SNA_Settings(bpy.types.PropertyGroup):

    addon: bpy.props.PointerProperty(type=SNA_AddonSettings)

    dev: bpy.props.PointerProperty(type=SNA_DevSettings)

    ui: bpy.props.PointerProperty(type=SNA_UISettings)

    def execute(self, node_id, globals, locals):
        nodes = [node for tree in scripting_node_trees() for node in tree.nodes]
        for node in nodes:
            if node.id == node_id:
                node._execute(globals, locals)
                return


def register():
    bpy.types.Scene.sna = bpy.props.PointerProperty(type=SNA_Settings)


def unregister():
    del bpy.types.Scene.sna
