import bpy

from ....core.context import NodeError
from ....sockets.spec import BlendData, Integer, String
from ._property_field import PropertyFieldNode

STYLES = [
    ("FIELD", "Field", "A one-line text field", "SYNTAX_OFF", 0),
    ("TEXTBOX", "Text Box", "A text field over several lines", "ALIGN_JUSTIFY", 1),
    (
        "SEARCH",
        "Search",
        "A field that suggests the names of a collection's items (objects, ...)",
        "VIEWZOOM",
        2,
    ),
]


class SNA_Node_TextField(PropertyFieldNode, bpy.types.Node):
    """Draw a string property as a text field, a text box over several lines
    or a search field suggesting names."""

    bl_idname = "SNA_Node_TextField"
    bl_label = "Text Field"
    sn_property_references = {"prop": "STRING"}
    blender_prop_types = {"STRING"}

    style: bpy.props.EnumProperty(name="Style", items=STYLES)

    def socket_specs(self):
        inputs, outputs = super().socket_specs()
        extra = [String("placeholder", "Placeholder")]
        if self.style == "TEXTBOX":
            extra.append(Integer("lines", "Lines", default=3))
        if self.style == "SEARCH":
            extra.append(BlendData("search", "Search In", collection=True))
        # after Text and Icon, before the property's own inputs
        return inputs[:3] + extra + inputs[3:], outputs

    def draw(self, context, layout):
        layout.prop(self, "style", text="")
        super().draw(context, layout)

    def prop_arguments(self, ctx):
        args = super().prop_arguments(ctx)
        placeholder = self.socket("placeholder")
        if placeholder.is_linked or placeholder.value:
            args.append(f"placeholder={ctx.input('placeholder')}")
        return args

    def emit(self, ctx):
        if self.style == "FIELD":
            return super().emit(ctx)
        data, name = self.property_target(ctx)
        if self.style == "TEXTBOX":
            # a text box has no label or icon: a label above it
            label = ""
            if self.socket("text").is_linked or self.socket("text").value:
                label = f"{ctx.layout}.label(text={ctx.input('text')})"
            args = [ctx.layout, data, repr(name), ctx.input("lines")]
            if self.socket("placeholder").is_linked or self.socket("placeholder").value:
                args.append(ctx.input("placeholder"))
            ctx.code(f"""
                {ctx.join([label])}
                {ctx.helper("sn_textbox")}({", ".join(args)})
                {ctx.flow("next")}
            """)
            return
        # prop_search takes the collection as its owner and attribute name
        if not ctx.is_linked("search"):
            raise NodeError("Connect the collection to search, e.g. all objects")
        collection = ctx.input("search")
        owner, dot, attribute = collection.rpartition(".")
        if not dot or not attribute.isidentifier():
            raise NodeError("Search In needs a collection of Blender data")
        args = [data, repr(name), owner, repr(attribute)]
        args += self.prop_arguments(ctx)
        ctx.code(f"""
            {ctx.layout}.prop_search({", ".join(args)})
            {ctx.flow("next")}
        """)
