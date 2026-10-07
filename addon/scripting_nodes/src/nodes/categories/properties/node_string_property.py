import bpy

from ._property_base import PropertyNode

STRING_SUBTYPES = [
    ("NONE", "None", "Plain string"),
    ("FILE_PATH", "File Path", "File path selector"),
    ("DIR_PATH", "Directory Path", "Directory path selector"),
    ("FILE_NAME", "File Name", "File name"),
    ("BYTE_STRING", "Byte String", "Byte string"),
    ("PASSWORD", "Password", "Password (hidden)"),
]


class SNA_Node_StringProperty(PropertyNode, bpy.types.Node):
    bl_idname = "SNA_Node_StringProperty"
    bl_label = "String Property"
    bpy_type = "StringProperty"
    data_type = "ScriptingStringSocket"

    prop_label: bpy.props.StringProperty(name="Label", default="My String")
    prop_default: bpy.props.StringProperty(name="Default")
    prop_maxlen: bpy.props.IntProperty(
        name="Max Length", description="Maximum length (0: unlimited)", min=0
    )
    prop_subtype: bpy.props.EnumProperty(items=STRING_SUBTYPES, name="Subtype")

    def property_args(self, ctx):
        args = [f"default={self.prop_default!r}"]
        if self.prop_maxlen > 0:
            args.append(f"maxlen={self.prop_maxlen}")
        if self.prop_subtype != "NONE":
            args.append(f"subtype={self.prop_subtype!r}")
        return args

    def draw_settings(self, layout):
        layout.prop(self, "prop_default")
        layout.prop(self, "prop_maxlen")
        layout.prop(self, "prop_subtype")
