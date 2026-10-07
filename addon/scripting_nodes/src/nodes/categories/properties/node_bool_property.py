import bpy

from ._property_base import PropertyNode


class SNA_Node_BoolProperty(PropertyNode, bpy.types.Node):
    bl_idname = "SNA_Node_BoolProperty"
    bl_label = "Boolean Property"
    bpy_type = "BoolProperty"
    data_type = "ScriptingBooleanSocket"

    prop_label: bpy.props.StringProperty(name="Label", default="My Boolean")
    prop_default: bpy.props.BoolProperty(name="Default")

    def property_args(self, ctx):
        return [f"default={self.prop_default}"]

    def draw_settings(self, layout):
        layout.prop(self, "prop_default")
