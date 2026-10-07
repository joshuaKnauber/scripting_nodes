import bpy

from ._property_base import PropertyNode

FLOAT_SUBTYPES = [
    ("NONE", "None", "Plain number"),
    ("PIXEL", "Pixel", "Pixel value"),
    ("UNSIGNED", "Unsigned", "Unsigned number"),
    ("PERCENTAGE", "Percentage", "Percentage value"),
    ("FACTOR", "Factor", "Factor value (0-1)"),
    ("ANGLE", "Angle", "Angle value"),
    ("TIME", "Time", "Time value"),
    ("TIME_ABSOLUTE", "Time Absolute", "Absolute time value"),
    ("DISTANCE", "Distance", "Distance value"),
    ("DISTANCE_CAMERA", "Distance Camera", "Camera distance"),
    ("POWER", "Power", "Power value"),
    ("TEMPERATURE", "Temperature", "Temperature value"),
]

FLOAT_UNITS = [
    ("NONE", "None", "No unit"),
    ("LENGTH", "Length", "Length unit"),
    ("AREA", "Area", "Area unit"),
    ("VOLUME", "Volume", "Volume unit"),
    ("ROTATION", "Rotation", "Rotation unit"),
    ("TIME", "Time", "Time unit"),
    ("TIME_ABSOLUTE", "Time Absolute", "Absolute time unit"),
    ("VELOCITY", "Velocity", "Velocity unit"),
    ("ACCELERATION", "Acceleration", "Acceleration unit"),
    ("MASS", "Mass", "Mass unit"),
    ("CAMERA", "Camera", "Camera unit"),
    ("POWER", "Power", "Power unit"),
    ("TEMPERATURE", "Temperature", "Temperature unit"),
]

FLOAT_MIN, FLOAT_MAX = -3.402823e38, 3.402823e38
# limits beyond these count as "no limit"
_UNLIMITED = 3.4e38


def float_limit_args(node):
    """min/max, soft limits, step and precision of float properties."""
    args = []
    if node.prop_min > -_UNLIMITED:
        args.append(f"min={node.prop_min!r}")
    if node.prop_max < _UNLIMITED:
        args.append(f"max={node.prop_max!r}")
    args += [
        f"soft_min={node.prop_soft_min!r}",
        f"soft_max={node.prop_soft_max!r}",
        f"step={node.prop_step}",
        f"precision={node.prop_precision}",
    ]
    return args


def draw_float_limits(node, layout):
    col = layout.column(align=True)
    col.label(text="Hard Limits")
    row = col.row(align=True)
    row.prop(node, "prop_min")
    row.prop(node, "prop_max")
    col = layout.column(align=True)
    col.label(text="Soft Limits")
    row = col.row(align=True)
    row.prop(node, "prop_soft_min")
    row.prop(node, "prop_soft_max")
    layout.prop(node, "prop_step")
    layout.prop(node, "prop_precision")


class SNA_Node_FloatProperty(PropertyNode, bpy.types.Node):
    bl_idname = "SNA_Node_FloatProperty"
    bl_label = "Float Property"
    bpy_type = "FloatProperty"
    data_type = "ScriptingFloatSocket"

    prop_label: bpy.props.StringProperty(name="Label", default="My Float")
    prop_default: bpy.props.FloatProperty(name="Default")
    prop_subtype: bpy.props.EnumProperty(items=FLOAT_SUBTYPES, name="Subtype")
    prop_unit: bpy.props.EnumProperty(items=FLOAT_UNITS, name="Unit")
    prop_min: bpy.props.FloatProperty(name="Min", default=FLOAT_MIN)
    prop_max: bpy.props.FloatProperty(name="Max", default=FLOAT_MAX)
    prop_soft_min: bpy.props.FloatProperty(name="Soft Min", default=0.0)
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

    def property_args(self, ctx):
        args = [f"default={self.prop_default!r}"]
        args += float_limit_args(self)
        if self.prop_subtype != "NONE":
            args.append(f"subtype={self.prop_subtype!r}")
        if self.prop_unit != "NONE":
            args.append(f"unit={self.prop_unit!r}")
        return args

    def draw_settings(self, layout):
        layout.prop(self, "prop_default")
        draw_float_limits(self, layout)
        layout.prop(self, "prop_subtype")
        layout.prop(self, "prop_unit")
