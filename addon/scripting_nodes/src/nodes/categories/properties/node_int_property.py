import bpy

from ._property_base import PropertyNode

INT_SUBTYPES = [
    ("NONE", "None", "Plain number"),
    ("PIXEL", "Pixel", "Pixel value"),
    ("UNSIGNED", "Unsigned", "Unsigned number"),
    ("PERCENTAGE", "Percentage", "Percentage value"),
    ("FACTOR", "Factor", "Factor value"),
    ("TIME", "Time", "Time value (frames)"),
    ("TIME_ABSOLUTE", "Time Absolute", "Absolute time value"),
]

INT_MIN, INT_MAX = -(2**31), 2**31 - 1


class SNA_Node_IntProperty(PropertyNode, bpy.types.Node):
    bl_idname = "SNA_Node_IntProperty"
    bl_label = "Integer Property"
    bpy_type = "IntProperty"
    data_type = "ScriptingIntegerSocket"

    prop_label: bpy.props.StringProperty(name="Label", default="My Integer")
    prop_default: bpy.props.IntProperty(name="Default")
    prop_min: bpy.props.IntProperty(name="Min", default=INT_MIN)
    prop_max: bpy.props.IntProperty(name="Max", default=INT_MAX)
    prop_soft_min: bpy.props.IntProperty(name="Soft Min", default=0)
    prop_soft_max: bpy.props.IntProperty(name="Soft Max", default=100)
    prop_step: bpy.props.IntProperty(name="Step", default=1, min=1, max=100)
    prop_subtype: bpy.props.EnumProperty(items=INT_SUBTYPES, name="Subtype")

    def property_args(self, ctx):
        args = [f"default={self.prop_default}"]
        if self.prop_min > INT_MIN:
            args.append(f"min={self.prop_min}")
        if self.prop_max < INT_MAX:
            args.append(f"max={self.prop_max}")
        args += [
            f"soft_min={self.prop_soft_min}",
            f"soft_max={self.prop_soft_max}",
            f"step={self.prop_step}",
        ]
        if self.prop_subtype != "NONE":
            args.append(f"subtype={self.prop_subtype!r}")
        return args

    def draw_settings(self, layout):
        layout.prop(self, "prop_default")
        row = layout.row(align=True)
        row.prop(self, "prop_min")
        row.prop(self, "prop_max")
        row = layout.row(align=True)
        row.prop(self, "prop_soft_min")
        row.prop(self, "prop_soft_max")
        layout.prop(self, "prop_step")
        layout.prop(self, "prop_subtype")
