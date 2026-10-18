"""Viewport Draw: draws in an editor every time it redraws, with the Draw
nodes connected to it (a draw handler, `SpaceView3D.draw_handler_add`)."""

import bpy

from ....core import naming
from ....sockets.spec import Boolean, Logic
from ...base_node import ScriptingBaseNode

SPACES = {
    "VIEW_3D": ("3D Viewport", "SpaceView3D"),
    "IMAGE_EDITOR": ("Image Editor", "SpaceImageEditor"),
    "NODE_EDITOR": ("Node Editor", "SpaceNodeEditor"),
    "SEQUENCE_EDITOR": ("Video Sequencer", "SpaceSequenceEditor"),
    "CLIP_EDITOR": ("Movie Clip Editor", "SpaceClipEditor"),
}


class SNA_Node_ViewportDraw(ScriptingBaseNode, bpy.types.Node):
    """Draw lines, shapes, text and images in an editor, every time it
    redraws. Use Redraw after changing what it draws."""

    bl_idname = "SNA_Node_ViewportDraw"
    bl_label = "Viewport Draw"
    bl_width_default = 220
    sn_root = True

    editor: bpy.props.EnumProperty(
        name="Editor",
        items=[(key, label, "") for key, (label, _) in SPACES.items()],
    )
    draw_in: bpy.props.EnumProperty(
        name="Draw",
        items=[
            (
                "SCENE",
                "In the Scene",
                "In the editor's own space (3D locations in the 3D Viewport), "
                "behind objects where they're in front",
            ),
            ("OVERLAY", "On Top", "In pixels of the editor, on top of everything"),
        ],
    )
    in_front: bpy.props.BoolProperty(
        name="In Front",
        description="Draw in front of objects instead of being hidden by them",
    )

    def socket_specs(self):
        return [Boolean("enabled", "Enabled", default=True)], [Logic("draw", "Draw")]

    def sn_names(self):
        base = naming.snake(self.label) if self.label else "viewport"
        return [naming.Symbol("function", f"draw_{base}")]

    def draw(self, context, layout):
        layout.prop(self, "editor", text="")
        layout.prop(self, "draw_in", expand=True)
        if self.draw_in == "SCENE" and self.editor == "VIEW_3D":
            layout.prop(self, "in_front")

    def emit(self, ctx):
        name = ctx.name("function")
        check = ""
        if not ctx.is_default("enabled", True):
            check = f"""
                if not {ctx.input("enabled")}:
                    return
            """
        # 3D drawing is hidden behind objects unless In Front
        depth = (
            self.draw_in == "SCENE" and self.editor == "VIEW_3D" and not self.in_front
        )
        depth_on = 'gpu.state.depth_test_set("LESS_EQUAL")' if depth else ""
        depth_off = 'gpu.state.depth_test_set("NONE")' if depth else ""
        ctx.imports("import gpu")
        ctx.module(f"""
            def {name}():
                {ctx.join([check])}
                gpu.state.blend_set("ALPHA")
                {ctx.join([depth_on])}
                {ctx.flow("draw")}
                {ctx.join([depth_off])}
                gpu.state.blend_set("NONE")
        """)
        space = SPACES[self.editor][1]
        draw_type = "POST_VIEW" if self.draw_in == "SCENE" else "POST_PIXEL"
        helper = ctx.helper("add_draw_handler")
        ctx.on_register(f"{helper}(bpy.types.{space}, {name}, {draw_type!r})")
