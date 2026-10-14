import bpy

from ._property_field import PropertyFieldNode

STYLES = [
    ("FIELD", "Dropdown", "A dropdown, or a row of buttons with Expand", "PRESET", 0),
    (
        "ICONS",
        "Icon View",
        "Large previews of the items' icons (custom icons look best)",
        "IMAGE_DATA",
        2,
    ),
]


class SNA_Node_EnumMenu(PropertyFieldNode, bpy.types.Node):
    """Draw an enum property as a dropdown, a row of buttons or large icon
    previews."""

    bl_idname = "SNA_Node_EnumMenu"
    bl_label = "Enum Menu"
    sn_property_references = {"prop": "ENUM"}
    blender_prop_types = {"ENUM"}
    field_options = (("expand", False), ("icon_only", False))

    style: bpy.props.EnumProperty(name="Style", items=STYLES)
    expand: bpy.props.BoolProperty(
        name="Expand", description="Show every item as its own button"
    )
    icon_only: bpy.props.BoolProperty(
        name="Icon Only", description="Only draw the icons of the items"
    )
    show_labels: bpy.props.BoolProperty(
        name="Labels", description="Show the items' names under the icons"
    )
    scale: bpy.props.FloatProperty(
        name="Scale", description="Size of the icon", default=5.0, min=1.0, max=20.0
    )

    def draw(self, context, layout):
        layout.prop(self, "style", text="")
        if self.style == "FIELD":
            super().draw(context, layout)
            return
        self.draw_target(layout)
        row = layout.row(align=True)
        row.prop(self, "show_labels", toggle=True)
        row.prop(self, "scale")

    def emit(self, ctx):
        if self.style == "FIELD":
            return super().emit(ctx)
        data, name = self.property_target(ctx)
        args = [data, repr(name)]
        if self.show_labels:
            args.append("show_labels=True")
        args.append(f"scale={self.scale!r}")
        ctx.code(f"""
            {ctx.layout}.template_icon_view({", ".join(args)})
            {ctx.flow("next")}
        """)
