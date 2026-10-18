"""Node types under their old bl_idnames, so files saved before a rename
still load: Blender drops a node whose type isn't registered (its settings
too). They aren't in the add menu; versioning replaces them with the
renamed node (core/versioning.py `_renamed_nodes`)."""

import bpy

from .categories.data.boolean.node_boolean_math import SNA_Node_BooleanMath
from .categories.data.boolean.node_invert_boolean import SNA_Node_InvertBoolean


class SNA_BooleanMath(SNA_Node_BooleanMath, bpy.types.Node):
    bl_idname = "SNA_BooleanMath"
    sn_renamed_to = SNA_Node_BooleanMath.bl_idname


class SNA_InvertBoolean(SNA_Node_InvertBoolean, bpy.types.Node):
    bl_idname = "SNA_InvertBoolean"
    sn_renamed_to = SNA_Node_InvertBoolean.bl_idname
