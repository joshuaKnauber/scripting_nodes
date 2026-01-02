from ..nodes.references.reference_properties import (
    SNA_NodeReference,
)
from ...lib.utils.node_tree.scripting_node_trees import (
    node_by_id,
)
from .ui_settings.ui_properties import SNA_UISettings
from .sn_settings.dev_properties import SNA_DevSettings
from .addon_settings.addon_properties import SNA_AddonSettings
import bpy


class SNA_Settings(bpy.types.PropertyGroup):

    addon: bpy.props.PointerProperty(type=SNA_AddonSettings)

    dev: bpy.props.PointerProperty(type=SNA_DevSettings)

    ui: bpy.props.PointerProperty(type=SNA_UISettings)

    references: bpy.props.CollectionProperty(type=SNA_NodeReference)

    def execute(self, node_id, globals, locals):
        node = node_by_id(node_id)
        if node:
            node._execute(globals, locals)


def register():
    bpy.types.Scene.sna = bpy.props.PointerProperty(type=SNA_Settings)


def unregister():
    del bpy.types.Scene.sna
