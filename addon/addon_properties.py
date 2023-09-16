import bpy

from .references.reference_properties import SN_Nodes


class SN_AddonProperties(bpy.types.PropertyGroup):

    references: bpy.props.PointerProperty(type=SN_Nodes)

    show_node_code: bpy.props.BoolProperty(default=False, name="Show Node Code", description="Display the code of the selected node")

    show_node_refs: bpy.props.BoolProperty(default=False, name="Show Node References", description="Display the node reference structure")
