import bpy

from .info.info_properties import SN_AddonInfoProperties
from .references.reference_properties import SN_Nodes


class SN_AddonProperties(bpy.types.PropertyGroup):

    active_nodetree_index: bpy.props.IntProperty(default=0, name="Active Node Tree Index", description="The index of the active node tree", min=0)

    references: bpy.props.PointerProperty(type=SN_Nodes)

    info: bpy.props.PointerProperty(type=SN_AddonInfoProperties)

    show_node_code: bpy.props.BoolProperty(default=False, name="Show Node Code", description="Display the code of the selected node")

    show_node_refs: bpy.props.BoolProperty(default=False, name="Show Node References", description="Display the node reference structure")
