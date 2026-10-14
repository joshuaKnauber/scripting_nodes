import bpy

from ....sockets.spec import String
from ._property_field import PropertyFieldNode


class SNA_Node_PointerField(PropertyFieldNode, bpy.types.Node):
    """Draw a pointer property as a search field, or as Blender's
    data-block selector with New and Open buttons."""

    bl_idname = "SNA_Node_PointerField"
    bl_label = "Pointer Field"
    sn_property_references = {"prop": "POINTER"}
    blender_prop_types = {"POINTER"}

    style: bpy.props.EnumProperty(
        name="Style",
        items=[
            ("FIELD", "Field", "A search field", "VIEWZOOM", 0),
            (
                "SELECTOR",
                "Data-block Selector",
                "Blender's selector of data-blocks (materials, images, ...), "
                "with buttons to make a new one or open a file",
                "MATERIAL",
                1,
            ),
        ],
    )

    def socket_specs(self):
        inputs, outputs = super().socket_specs()
        if self.style == "SELECTOR":
            extra = [
                String("new", "New Operator", default=""),
                String("open", "Open Operator", default=""),
            ]
            inputs = inputs[:1] + extra + inputs[3:]  # no label or icon
        return inputs, outputs

    def draw(self, context, layout):
        layout.prop(self, "style", text="")
        if self.style == "FIELD":
            super().draw(context, layout)
        else:
            self.draw_target(layout)

    def emit(self, ctx):
        if self.style == "FIELD":
            return super().emit(ctx)
        data, name = self.property_target(ctx)
        args = [data, repr(name)]
        for key in ("new", "open"):
            socket = self.socket(key)
            if socket.is_linked or socket.value:
                args.append(f"{key}={ctx.input(key)}")
        ctx.code(f"""
            {ctx.layout}.template_ID({", ".join(args)})
            {ctx.flow("next")}
        """)
