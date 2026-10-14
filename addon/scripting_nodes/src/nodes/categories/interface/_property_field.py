"""Base of the UI field nodes (Checkbox, Number Field, Text Field, ...).

They all draw one property with `layout.prop(data, "name", ...)`; they only
differ in which property nodes they accept and in their display toggles.

    class SNA_Node_Checkbox(PropertyFieldNode, bpy.types.Node):
        sn_property_references = {"prop": "BOOLEAN"}
        field_options = (("toggle", False), ("invert_checkbox", False))
        toggle: bpy.props.BoolProperty(name="Toggle")
        ...
"""

import bpy

from ....sockets.spec import Icon, Interface, String
from ..._icon import icon_argument
from ..._property_target import PropertyTargetMixin
from ...base_node import ScriptingBaseNode


class PropertyFieldNode(PropertyTargetMixin, ScriptingBaseNode):
    bl_width_default = 200

    # (bool node property, Blender's default for it): the property becomes a
    # `name=value` argument of layout.prop() when it differs from the default
    field_options: tuple = ()

    emboss: bpy.props.BoolProperty(
        name="Emboss", description="Draw the field with an embossed look", default=True
    )

    def socket_specs(self):
        # the property's owner and path keys last, as one group
        inputs = [
            Interface(),
            String("text", "Text"),
            Icon(),
            *self.target_input_specs(),
        ]
        return inputs, [Interface("next")]

    def prop_arguments(self, ctx):
        args = []
        text = self.socket("text")
        # an empty label falls back to the property's own name
        if text.is_linked or text.value:
            args.append(f"text={ctx.input('text')}")
        icon = icon_argument(ctx)
        if icon:
            args.append(icon)
        for name, default in (("emboss", True),) + tuple(self.field_options):
            value = getattr(self, name)
            if value != default:
                args.append(f"{name}={value!r}")
        return args

    def emit(self, ctx):
        data, name = self.property_target(ctx)
        args = ", ".join([data, repr(name)] + self.prop_arguments(ctx))
        ctx.code(f"""
            {ctx.layout}.prop({args})
            {ctx.flow("next")}
        """)

    def draw(self, context, layout):
        self.draw_target(layout)
        row = layout.row(align=True)
        for name, _ in (("emboss", True),) + tuple(self.field_options):
            row.prop(self, name, toggle=True)
