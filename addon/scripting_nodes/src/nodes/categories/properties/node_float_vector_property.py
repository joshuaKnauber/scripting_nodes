import bpy

from ._property_base import PropertyNode
from .node_float_property import (
    FLOAT_MAX,
    FLOAT_MIN,
    draw_float_limits,
    float_limit_args,
)

VECTOR_SUBTYPES = [
    ("NONE", "None", "Plain vector"),
    ("COLOR", "Color", "Color vector (0-1 range)"),
    ("TRANSLATION", "Translation", "Translation vector"),
    ("DIRECTION", "Direction", "Direction vector"),
    ("VELOCITY", "Velocity", "Velocity vector"),
    ("ACCELERATION", "Acceleration", "Acceleration vector"),
    ("MATRIX", "Matrix", "Matrix vector"),
    ("EULER", "Euler", "Euler rotation"),
    ("QUATERNION", "Quaternion", "Quaternion rotation"),
    ("AXISANGLE", "Axis Angle", "Axis angle rotation"),
    ("XYZ", "XYZ", "XYZ coordinates"),
    ("COLOR_GAMMA", "Color Gamma", "Color with gamma correction"),
    ("LAYER", "Layer", "Layer bitflag"),
    ("LAYER_MEMBER", "Layer Member", "Layer membership"),
]

COLOR_SUBTYPES = {"COLOR", "COLOR_GAMMA"}


class SNA_Node_FloatVectorProperty(PropertyNode, bpy.types.Node):
    bl_idname = "SNA_Node_FloatVectorProperty"
    bl_label = "Float Vector Property"
    bpy_type = "FloatVectorProperty"

    prop_label: bpy.props.StringProperty(name="Label", default="My Vector")
    prop_size: bpy.props.IntProperty(
        name="Size", description="Number of components", default=3, min=1, max=4
    )
    prop_default_value: bpy.props.FloatVectorProperty(name="Default", size=4)
    prop_min: bpy.props.FloatProperty(name="Min", default=FLOAT_MIN)
    prop_max: bpy.props.FloatProperty(name="Max", default=FLOAT_MAX)
    prop_soft_min: bpy.props.FloatProperty(name="Soft Min", default=-1.0)
    prop_soft_max: bpy.props.FloatProperty(name="Soft Max", default=1.0)
    prop_step: bpy.props.IntProperty(
        name="Step",
        description="Step of increment/decrement in the UI (in 1/100)",
        default=3,
        min=1,
        max=100,
    )
    prop_precision: bpy.props.IntProperty(
        name="Precision",
        description="Displayed decimal digits",
        default=2,
        min=0,
        max=6,
    )
    prop_subtype: bpy.props.EnumProperty(items=VECTOR_SUBTYPES, name="Subtype")

    @property
    def data_type(self):
        if self.prop_subtype in COLOR_SUBTYPES and self.prop_size in (3, 4):
            return "ScriptingColorSocket"
        return "ScriptingVectorSocket"

    @property
    def prop_default(self):
        """Default value with `prop_size` components."""
        return tuple(self.prop_default_value[: self.prop_size])

    def property_args(self, ctx):
        values = ", ".join(repr(float(v)) for v in self.prop_default)
        if self.prop_size == 1:
            values += ","
        args = [f"default=({values})", f"size={self.prop_size}"]
        args += float_limit_args(self)
        if self.prop_subtype != "NONE":
            args.append(f"subtype={self.prop_subtype!r}")
        return args

    def draw_settings(self, layout):
        layout.prop(self, "prop_size")
        col = layout.column(align=True)
        col.label(text="Default")
        for i in range(self.prop_size):
            col.prop(self, "prop_default_value", index=i, text="XYZW"[i])
        draw_float_limits(self, layout)
        layout.prop(self, "prop_subtype")
