"""Nodes drawing inside a Viewport Draw flow. Each writes one call of a
drawing helper (core/helpers.py DRAW_HELPERS); points are 2D pixels when
drawing on top, 3D locations when drawing in the 3D scene."""

import bpy

from ....sockets.spec import (
    BlendData,
    Color,
    Flow,
    Float,
    Integer,
    List,
    String,
    Vector,
)
from ...base_node import ScriptingBaseNode

WHITE = (1.0, 1.0, 1.0, 1.0)


def _color():
    return Color("color", "Color", default=WHITE, alpha=True)


class DrawNode(ScriptingBaseNode):
    """A call of helper `sn_helper` with the node's inputs: positional ones
    always, `(keyword, input key, default)` ones only when changed."""

    sn_helper = ""
    sn_positional: tuple = ()
    sn_keywords: tuple = ()

    def extra_keywords(self, ctx) -> list:
        """Settings of the node (not inputs) as `name=value`."""
        return []

    def emit(self, ctx):
        args = [ctx.input(key) for key in self.sn_positional]
        args += [
            ctx.keyword(name, key, default) for name, key, default in self.sn_keywords
        ]
        args += self.extra_keywords(ctx)
        ctx.code(f"""
            {ctx.helper(self.sn_helper)}({ctx.args(*args)})
            {ctx.flow("next")}
        """)


class SNA_Node_DrawLines(DrawNode, bpy.types.Node):
    """Lines through a list of points: connected, closed into a shape, or
    in pairs."""

    bl_idname = "SNA_Node_DrawLines"
    bl_label = "Draw Lines"
    sn_inputs = [
        Flow(),
        List("points", "Points"),
        _color(),
        Float("width", "Width", default=2.0),
    ]
    sn_outputs = [Flow("next")]
    sn_helper = "draw_lines"
    sn_positional = ("points",)
    sn_keywords = (("color", "color", WHITE), ("width", "width", 2.0))

    mode: bpy.props.EnumProperty(
        name="Lines",
        items=[
            ("LINE_STRIP", "Connected", "One line through all points"),
            ("LINE_LOOP", "Closed", "Back to the first point at the end"),
            ("LINES", "Pairs", "A line for every two points"),
        ],
    )

    def draw(self, context, layout):
        layout.prop(self, "mode", text="")

    def extra_keywords(self, ctx):
        return [f"mode={self.mode!r}"] if self.mode != "LINE_STRIP" else []


class SNA_Node_DrawPoints(DrawNode, bpy.types.Node):
    """A dot at each point of a list."""

    bl_idname = "SNA_Node_DrawPoints"
    bl_label = "Draw Points"
    sn_inputs = [
        Flow(),
        List("points", "Points"),
        _color(),
        Float("size", "Size", default=6.0),
    ]
    sn_outputs = [Flow("next")]
    sn_helper = "draw_points"
    sn_positional = ("points",)
    sn_keywords = (("color", "color", WHITE), ("size", "size", 6.0))


class SNA_Node_DrawPolygon(DrawNode, bpy.types.Node):
    """A filled shape with a list of points as its outline."""

    bl_idname = "SNA_Node_DrawPolygon"
    bl_label = "Draw Polygon"
    sn_inputs = [Flow(), List("points", "Points"), _color()]
    sn_outputs = [Flow("next")]
    sn_helper = "draw_polygon"
    sn_positional = ("points",)
    sn_keywords = (("color", "color", WHITE),)


class SNA_Node_DrawRectangle(DrawNode, bpy.types.Node):
    """A rectangle in pixels, from its bottom left corner: filled or as an
    outline."""

    bl_idname = "SNA_Node_DrawRectangle"
    bl_label = "Draw Rectangle"
    sn_outputs = [Flow("next")]
    sn_helper = "draw_rectangle"
    sn_positional = ("position", "size")

    fill: bpy.props.BoolProperty(name="Fill", default=True)

    def socket_specs(self):
        inputs = [
            Flow(),
            Vector("position", "Position", default=(20.0, 20.0), dimension=2),
            Vector("size", "Size", default=(200.0, 100.0), dimension=2),
            _color(),
            Float("width", "Width", default=2.0, enabled=not self.fill),
        ]
        return inputs, self.sn_outputs

    @property
    def sn_keywords(self):
        keywords = [("color", "color", WHITE)]
        return tuple(keywords if self.fill else keywords + [("width", "width", 2.0)])

    def draw(self, context, layout):
        layout.prop(self, "fill")

    def extra_keywords(self, ctx):
        return [] if self.fill else ["fill=False"]


class SNA_Node_DrawCircle(DrawNode, bpy.types.Node):
    """A circle: in pixels when drawing on top, in the scene facing
    Normal when drawing in 3D."""

    bl_idname = "SNA_Node_DrawCircle"
    bl_label = "Draw Circle"
    sn_outputs = [Flow("next")]
    sn_helper = "draw_circle"
    sn_positional = ("center", "radius")

    fill: bpy.props.BoolProperty(name="Fill")

    def socket_specs(self):
        inputs = [
            Flow(),
            Vector("center", "Center", default=(0.0, 0.0, 0.0)),
            Float("radius", "Radius", default=1.0),
            _color(),
            Float("width", "Width", default=2.0, enabled=not self.fill),
            Integer("segments", "Segments", default=32),
            Vector("normal", "Normal", default=(0.0, 0.0, 1.0)),
        ]
        return inputs, self.sn_outputs

    @property
    def sn_keywords(self):
        keywords = [("color", "color", WHITE)]
        if not self.fill:
            keywords.append(("width", "width", 2.0))
        keywords += [
            ("segments", "segments", 32),
            ("normal", "normal", (0.0, 0.0, 1.0)),
        ]
        return tuple(keywords)

    def draw(self, context, layout):
        layout.prop(self, "fill")

    def extra_keywords(self, ctx):
        return ["fill=True"] if self.fill else []


class SNA_Node_DrawText(DrawNode, bpy.types.Node):
    """Text in pixels, sized like Blender's interface. For a 3D location,
    get its Position with Location to Screen."""

    bl_idname = "SNA_Node_DrawText"
    bl_label = "Draw Text"
    sn_inputs = [
        Flow(),
        String("text", "Text", default="Text"),
        Vector("position", "Position", default=(20.0, 20.0), dimension=2),
        Float("size", "Size", default=16.0),
        _color(),
    ]
    sn_outputs = [Flow("next")]
    sn_helper = "draw_text"
    sn_positional = ("text", "position")
    sn_keywords = (("size", "size", 16.0), ("color", "color", WHITE))

    align: bpy.props.EnumProperty(
        name="Align",
        items=[("LEFT", "Left", ""), ("CENTER", "Center", ""), ("RIGHT", "Right", "")],
    )
    shadow: bpy.props.BoolProperty(name="Shadow", description="A dark shadow behind it")

    def draw(self, context, layout):
        row = layout.row()
        row.prop(self, "align", expand=True)
        layout.prop(self, "shadow")

    def extra_keywords(self, ctx):
        keywords = [f"align={self.align!r}"] if self.align != "LEFT" else []
        return keywords + (["shadow=True"] if self.shadow else [])


class SNA_Node_DrawImage(DrawNode, bpy.types.Node):
    """An image in pixels, from its bottom left corner."""

    bl_idname = "SNA_Node_DrawImage"
    bl_label = "Draw Image"
    sn_inputs = [
        Flow(),
        BlendData("image", "Image", "Image"),
        Vector("position", "Position", default=(20.0, 20.0), dimension=2),
        Vector("size", "Size", default=(128.0, 128.0), dimension=2),
        Float("opacity", "Opacity", default=1.0),
    ]
    sn_outputs = [Flow("next")]
    sn_helper = "draw_image"
    sn_positional = ("image", "position", "size")
    sn_keywords = (("opacity", "opacity", 1.0),)


class SNA_Node_DrawObject(DrawNode, bpy.types.Node):
    """An object's mesh with its modifiers, where it is in the scene: as
    wireframe, faces or points. Draw it in the scene of the 3D Viewport."""

    bl_idname = "SNA_Node_DrawObject"
    bl_label = "Draw Object"
    sn_outputs = [Flow("next")]
    sn_helper = "draw_object"
    sn_positional = ("object",)

    style: bpy.props.EnumProperty(
        name="Style",
        items=[
            ("WIRE", "Wireframe", "The edges"),
            ("FACES", "Faces", "The filled faces"),
            ("POINTS", "Points", "The vertices"),
        ],
    )

    def socket_specs(self):
        inputs = [
            Flow(),
            BlendData("object", "Object", "Object"),
            _color(),
            Float("width", "Width", default=1.0, enabled=self.style == "WIRE"),
            Float("size", "Size", default=4.0, enabled=self.style == "POINTS"),
        ]
        return inputs, self.sn_outputs

    @property
    def sn_keywords(self):
        keywords = [("color", "color", WHITE)]
        if self.style == "WIRE":
            keywords.append(("width", "width", 1.0))
        if self.style == "POINTS":
            keywords.append(("size", "size", 4.0))
        return tuple(keywords)

    def draw(self, context, layout):
        layout.prop(self, "style", text="")

    def extra_keywords(self, ctx):
        return [f"style={self.style!r}"] if self.style != "WIRE" else []
